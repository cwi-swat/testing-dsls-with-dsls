"""Run the scriptless TESTAR cycle for one SUT (System Under Test).

The loop controls sequences, counters and stopping. TESTARSteps supplies each
step and delegates browser work to a session. Callers can supply other steps
or a browser backend; Playwright remains the default.
"""
from time import perf_counter
from browser_backend import BrowserBackend
from TESTARsteps import TESTARSteps
from reporting import (
    print_test_summary, print_performance_summary, print_sequence_start, print_sequence_summary,
    print_sequence_stop, print_action_result,
)


def testar(url, num_runs, length_sequence, filter_elements, preparations, oracles,
           *, backend: BrowserBackend = None, measure_timings=False, max_failures=5, steps=None):
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

        steps: Optional object providing the TESTARSteps methods and measurements.
            When supplied, it owns its backend, filters, preparations and oracles;
            the corresponding arguments above configure only the default steps.

        measure_timings: Print per-step durations and counts when True.
            Includes oracle time; sequence totals also include startup and cleanup.
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

    if backend is None:
        # Default is playwright
        from playwright_backend import PlaywrightBackend
        backend = PlaywrightBackend()

    if steps is None:
        # Default is TESTARSteps with the supplied backend, filters, preparations and oracles.
        steps = TESTARSteps(backend=backend, 
                            filters=filter_elements,
                            preparations=preparations, 
                            oracles=oracles)

    # Vanaf hier meten we de totale looptijd van de test. 
    # Include browser startup, preparations, oracle checks and closing every session.
    started_at = perf_counter()
    
    # Keep track of SUT oracle findings and other problems running the test.
    oracle_findings = []
    execution_failures = []
    sequence_stops = []
    sequence_results = []

    # OUTER_LOOP: Test num_runs test sequences of length length_sequence, each in a new browser session.
    for run_cnt in range(1, num_runs+1):
        sequence_started = perf_counter()
        sequence_phases = {}
        findings_before_sequence = len(oracle_findings)
        # START_SUT: The session owns the browser resources for this sequence.
        steps.begin_sequence(url)

        try:
            print_sequence_start(run_cnt, num_runs)
            
            timings = steps.performance
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

                step_started = perf_counter()
                completed_before = completed
                attempts_before = attempts
                findings_before = len(oracle_findings)
                step_checks = 0
                timings.reset()
                
                # DERIVE_ACTIONS: backend retries discovery + description together.
                possible_actions = steps.derive_actions()

                remaining_actions = list(possible_actions) #make a copy to remove skipped actions
                
                #SELECT and EXECUTE ACTION (and measure time)              
                with timings.measure('execution'):
                    result = None
                    # None: no action has been attempted yet. 
                    # execution_skipped: the selected action could not begin so choose another action from the same list. 
                    #          The remaining_actions list is updated to remove the skipped target.
                    # execution_succeeded: selected action was executed.
                    # execution_failed: the execution of the selected action resulted in a failure, but partial effects are possible, 
                    #         so stop here and start new inner loop.
                    while remaining_actions and (result is None or result.status == 'execution_skipped'):
                        
                        selected_action = steps.select_action(remaining_actions)

                        attempts += 1

                        result = steps.execute_action(selected_action)
                        message = print_action_result(
                            result, selected_action, sequence=run_cnt, attempt=attempts,
                            action_number=completed + 1, length_sequence=length_sequence)
                        if result.status == 'execution_failed':
                            execution_failures.append(message)

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
                    # Read the current page after execution, including partial effects of a failed action.
                    with timings.measure('oracles'):
                        step_checks = steps.check_oracles(oracle_findings, run_cnt, attempts)
                    oracle_checks += step_checks
                
                # Collect and print the performance summary for this step, including counts and timings.
                for phase, item in timings.measurements.items():
                    if '.' not in phase:
                        sequence_phases[phase] = sequence_phases.get(phase, 0.0) + item['seconds']
                # A skipped target can cause several attempts within this one derivation step.
                element_count = steps.actionable_element_count
                print_performance_summary(timings,
                    f'run {run_cnt}, attempts {attempts_before + 1}-{attempts}'
                    if attempts > attempts_before else f'run {run_cnt}, no execution attempt',
                    counts={'elements': element_count if element_count is not None else 'unknown',
                            'possible_actions': len(possible_actions),
                            'completed': completed - completed_before, 'attempts': attempts - attempts_before,
                            'oracle_checks': step_checks, 'oracle_findings': len(oracle_findings) - findings_before},
                    total_seconds=perf_counter() - step_started)
            
            # Stop the sequence when no reachable candidate remains or after max_failures consecutive failed attempts.
            if consecutive_execution_failures >= max_failures:
                reason = print_sequence_stop(run_cnt, f"{max_failures} consecutive failed attempts.")
                sequence_stops.append(reason)
            
            # Record the results of this sequence, including counts and timings. 
            sequence_results.append({
                'sequence': run_cnt, 'completed': completed, 'attempts': attempts,
                'oracle_checks': oracle_checks,
                'oracle_findings': len(oracle_findings) - findings_before_sequence,
                'phases': sequence_phases,
            })
        finally:
            # Also runs for discovery, execution, oracle errors and Ctrl+C.
            steps.end_sequence()
        sequence_results[-1]['total_seconds'] = perf_counter() - sequence_started
        print_sequence_summary(sequence_results[-1], show_timings=measure_timings)

    # Report oracle findings and execution problems after all sequences.
    print_test_summary(url, num_runs, length_sequence, oracle_findings,
                       execution_failures, sequence_stops, sequence_results=sequence_results,
                       total_seconds=perf_counter() - started_at)

