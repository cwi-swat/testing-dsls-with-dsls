"""Run the scriptless TESTAR cycle for one SUT (System Under Test).

The core controls the test sequence; the browser session handles browser APIs.
Playwright is the default, but callers can supply another BrowserBackend.
The active loop describes actions for all actionable elements, chooses one
description, and asks the session to execute it. The default browser backend is Playwright.
"""
import random
from performance import PerformanceMeasurements
from browser_backend import BrowserBackend
from reporting import (
    print_test_summary, print_performance_summary, print_sequence_start,
    print_sequence_stop, print_action_result, print_oracle_finding, print_oracle_error,
)


def _resolve_backend(backend):
    """Resolve the supplied backend, defaulting to a new Playwright backend.

    Use None as the default to avoid sharing a backend instance across calls.
    Import Playwright only when needed, so other backends can run without it.
    """
    if backend is None: 
        from playwright_backend import PlaywrightBackend
        return PlaywrightBackend()
    return backend


def start_SUT(website_url, preparations, *, backend: BrowserBackend = None):
    """Start the SUT and return the session used throughout one sequence.

    Each preparation receives session.page, the backend-specific browser
    object (currently a Playwright Page). It can log in or wait for content.
    Their implementation must match the selected backend. If a preparation
    fails, close the newly created session before propagating the error.
    """
    # Choose the default only here; subsequent steps use the returned session.
    backend = _resolve_backend(backend)
    session = backend.start(website_url)
    try:
        for prepare in preparations:
            prepare(session.page)
    except BaseException:
        session.close()
        raise
    return session


def derive_actions(session, filter_elements):
    """Return a list of action descriptions that can be chosen and executed.
    """
    return session.derive_actions(filter_elements)


def select_action(possible_actions):
    """Choose one action description randomly from the supplied list.

    Selection does not execute the action. The loop checks that the list is
    nonempty before calling this function.
    """
    selected_action_id = int(random.randint(0, len(possible_actions)-1))
    return possible_actions[selected_action_id]


def execute_action_description(session, description, value=None, *, run_cnt=None,
                               attempt=None, action_number=None, length_sequence=None,
                               execution_failures=None):
    """Execute one description, report its outcome and return the ActionResult.

    value=None uses the description's input strategy; an explicit string is
    used unchanged. Optional context supplies sequence/attempt numbers for
    messages. Execution failures are recorded separately from oracle findings.
    Counters and remaining candidates are managed by the TESTAR loop.
    """
    result = session.execute_action_description(description, value=value)
    message = print_action_result(
        result, description, sequence=run_cnt, attempt=attempt,
        action_number=action_number, length_sequence=length_sequence)
    if result.status == 'execution_failed' and execution_failures is not None:
        execution_failures.append(message)
    return result


def check_oracles(driver, oracles, oracle_findings, seq, acc):

    """Run each oracle on the backend-specific browser object after an action.

    driver is the historical parameter name for the browser object,
    currently a Playwright Page.
    AssertionError means an oracle found a violation: print it, record the
    sequence/attempt numbers, and continue with the remaining oracles.
    Other exceptions are not recorded as violations in this implementation:
    print them and pause for terminal input before continuing.
    Return the number of oracle calls, including calls that report a finding
    or an error. With an empty oracle list, return zero.
    """
    checked = 0
    for oracle in oracles:
        checked += 1
        try:
            oracle(driver)
        except AssertionError as e:
            oracle_findings.append(print_oracle_finding(oracle.__name__, e, seq, acc))
        except Exception as e:
            print_oracle_error(oracle.__name__, e)
            # Add an interactive pause for an unexpected error.
            stop = input("")
    return checked


def testar(url, num_runs, length_sequence, filter_elements, preparations, oracles,
           *, backend: BrowserBackend = None, measure_timings=False, max_failures=5):
    """Execute independent sequences of random GUI actions on one SUT.

    Parameters:
        url: Address of the application, including file:// for a local page.
        num_runs: Number of sequences; each starts a fresh browser session.
        length_sequence: Maximum number of successfully executed actions per
            sequence. Stop earlier if no reachable candidate remains.
        filter_elements: Functions receiving the backend-specific browser object
            as an argument and describing elements to exclude. Their
            return values use the selected backend's native element API.
        preparations: Functions receiving the backend-specific browser object
            as an argument, run once after opening the SUT in each sequence.
        oracles: Functions receiving the backend-specific browser object
            as an argument and asserting properties after every executed action.
        backend: Optional browser backend; None selects Playwright at startup.
            The * in the signature requires backend to be passed by name.

        measure_timings: Print per-step durations and counts when True.
            Startup and oracle time are not included.
        max_failures: Stop after this many consecutive failed attempts.
            Use a positive value. Successful actions reset the counter;
            skipped targets do not.

    Preparations, filters and oracles receive the session's backend-specific browser object.
    The active cycle is: get actionable elements and make action descriptions ->
    choose one -> check reachability -> execute it -> check oracles
    -> repeat. Blocked or disabled targets are skipped without counting an action. Stop
    the sequence when no candidate can be executed. Reachability scrolling
    can trigger page events; it is part of preparing the selected action.

    The final report contains recorded oracle assertion failures across all
    sequences, execution failures and early stops. After a failed attempt,
    check oracles on the current page, then discover again on the next step;
    partial effects are possible. Stop after
    max_failures consecutive failures. Unexpected errors propagate, but the
    session is always closed. No findings does not prove correctness.
    """
    # Keep track of SUT oracle findings and other problems running the test.
    oracle_findings = []
    execution_failures = []
    sequence_stops = []
    sequence_results = []

    # OUTER_LOOP: Test num_runs test sequences of length length_sequence, each in a new browser session.
    for run_cnt in range(1, num_runs+1):
        # START_SUT: The session owns the browser resources for this sequence.
        session = start_SUT(url, preparations, backend=backend)

        try:
            print_sequence_start(run_cnt, num_runs)
            
            # Share the performance measurements with the browser session.
            timings = getattr(session, 'performance', None)
            if timings is None:
                timings = PerformanceMeasurements()
                session.performance = timings
            timings.enabled = measure_timings
            
            oracle_checks = 0 # Number of oracle calls in this sequence.
            completed = 0 # Successfully executed actions.
            consecutive_execution_failures = 0 # Failed attempts in a row; reset after success.
            attempts = 0 # All attempts: succeeded, failed or skipped execution.
            sequence_stopped = False # Stop explicitly when one candidate list is exhausted.

            # INNER_LOOP: Create a test sequence with length_sequence actions.
            # Stop after max_failures consecutive attempts with status 'execution_failed' (i.e. timeouts, detached elements, 
            # navigation during execution, or a target selector that no longer matches exactly one element.)
            # Stop when no candidate actions remain.
            while (completed < length_sequence 
                   and consecutive_execution_failures < max_failures 
                   and not sequence_stopped):

                timings.reset()
                
                # DERIVE_ACTIONS: backend retries discovery + description together.
                possible_actions = derive_actions(session, filter_elements)

                remaining_actions = list(possible_actions) #make a copy to remove skipped actions
                
                #SELECT and EXECUTE ACTION              
                with timings.measure('execution'):
                    result = None
                    # None: no action has been attempted yet. 
                    # execution_skipped: the selected action could not begin so choose another action from the same list. 
                    #          The remaining_actions list is updated to remove the skipped target.
                    # execution_succeeded: selected action was executed.
                    # execution_failed: the execution of the selected action resulted in a failure, but partial effects are possible, 
                    #         so stop here and start new inner loop.
                    while remaining_actions and (result is None or result.status == 'execution_skipped'):
                        
                        selected_action = select_action(remaining_actions)

                        attempts += 1

                        result = execute_action_description(
                            session, selected_action, run_cnt=run_cnt, attempt=attempts,
                            action_number=completed + 1, length_sequence=length_sequence,
                            execution_failures=execution_failures)
                        
                        # Only a skipped target loses its actions; other outcomes
                        # keep the list intact and end this selection loop.
                        remaining_actions = [
                            action for action in remaining_actions
                            if result.status != 'execution_skipped'
                            or action['selector'] != selected_action['selector']
                        ]

                # Three outcomes of the SELECT and EXECUTE loop:
                if not remaining_actions:
                    # No derived action could begin, all skipped. Stop the sequence, but do not count this as a failure.
                    sequence_stopped = True
                    reason = print_sequence_stop(run_cnt, "no reachable action remains.")
                    sequence_stops.append(reason)
                elif result.status == 'execution_succeeded':
                    # Action completed: count it and reset consecutive failures.
                    completed += 1
                    consecutive_execution_failures = 0
                elif result.status == 'execution_failed':
                    # Execution failed: count the failure, not a completed action.
                    consecutive_execution_failures += 1

                # CHECK ORACLES after execution_succeeded and execution_failed; effects may have occurred.
                if not sequence_stopped:
                    print_performance_summary(timings, f'run {run_cnt}, attempt {attempts}: '
                                   f'{session.actionable_element_count} elements | {len(possible_actions)} actions')
                    # Oracles read the current page. The next iteration discovers
                    # fresh actions; never repeat a failed attempt automatically.
                    oracle_checks += check_oracles(
                        session.page, oracles, oracle_findings, run_cnt, attempts)
            if consecutive_execution_failures >= max_failures:
                reason = print_sequence_stop(
                    run_cnt, f"{max_failures} consecutive failed attempts.")
                sequence_stops.append(reason)
            sequence_results.append({
                'sequence': run_cnt, 'completed': completed, 'attempts': attempts,
                'oracle_checks': oracle_checks,
            })
        finally:
            # Also runs for discovery, execution, oracle errors and Ctrl+C.
            session.close()

    # Report oracle findings and execution problems after all sequences.
    print_test_summary(url, num_runs, length_sequence, oracle_findings,
                       execution_failures, sequence_stops, sequence_results=sequence_results)

