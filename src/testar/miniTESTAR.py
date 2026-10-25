"""Run the scriptless TESTAR cycle for one SUT (System Under Test).

The loop controls sequences, counters and stopping. TESTARSteps supplies each
step and delegates browser work to a session. The timing flag selects an
optional performance wrapper; Playwright remains the default backend.
"""
from browser_backend import BrowserBackend
from TESTAR_steps import TESTARSteps
from performance_steps import PerformanceTESTARSteps
from reporting import (
    print_sequence_start,
    print_sequence_stop, print_action_result,
)

def configure_steps(*, filter_elements, preparations, oracles,
                    backend: BrowserBackend = None, measure_timings=False):
    """Choose the backend and compose the steps from the test settings.

    Keep defaults and optional wrappers here so the test loop only calls steps.
    This function does not start the browser or the test.
    """
    if backend is None:
        # Import the default backend only when no backend was supplied.
        from playwright_backend import PlaywrightBackend
        backend = PlaywrightBackend()

    steps = TESTARSteps(backend=backend, filters=filter_elements,
                        preparations=preparations, oracles=oracles)

    if measure_timings:
        steps = PerformanceTESTARSteps(steps, detailed=True)

    return steps


def testar(*, url, num_runs, length_sequence, filter_elements, preparations, oracles,
           backend: BrowserBackend = None, measure_timings=False, max_failures=5):
    """Execute independent sequences of random GUI actions on one SUT.

    All arguments must be named so each test setup is explicit.

    Parameters:
        url: Address of the application, including file:// for a local page.
        num_runs: Number of sequences; each starts a fresh browser session.
        length_sequence: Maximum number of successfully executed actions per
            sequence. Stop earlier if candidates are exhausted or max_failures is reached.
        filter_elements: Functions receiving the backend-specific browser object
            as an argument and describing elements to exclude. Their
            return values use the selected backend's native element API.
        preparations: Functions receiving the backend-specific browser object
            as an argument, run once after opening the SUT in each sequence.
        oracles: Functions receiving the backend-specific browser object
            as an argument and asserting properties after successful or failed execution.
            Skipped actions do not trigger oracle checks.
        backend: Optional browser backend; None selects Playwright during configuration.
        measure_timings: Add a performance wrapper when True. With False,
            no timings are collected or reported. Measured totals include
            browser startup, preparations, oracle checks and cleanup, but exclude
            the final test summary.
        max_failures: Stop after this many consecutive failed attempts.
            Use a positive value. Successful actions reset the counter;
            skipped targets do not.
    """

    steps = configure_steps(
        filter_elements=filter_elements,
        preparations=preparations,
        oracles=oracles,
        backend=backend,
        measure_timings=measure_timings,
    )

    # Keep track of SUT oracle findings and other problems running the test.
    oracle_findings = []
    execution_failures = []
    sequence_stops = []
    sequence_results = []

    try:
        # Begin the whole test before starting its independent sequences.
        steps.begin_test()

        for run_cnt in range(1, num_runs+1):
            findings_before_sequence = len(oracle_findings)
            # START_SUT: The session owns the browser resources for this sequence.
            steps.begin_sequence(url)

            try:
                print_sequence_start(run_cnt, num_runs)

                oracle_checks = 0 # Number of oracle calls in this sequence.
                completed = 0 # Successfully executed actions.
                consecutive_execution_failures = 0 # Failed attempts in a row; reset after success.
                attempts = 0 # All attempts: succeeded, failed or skipped execution.
                sequence_stopped = False # Stop explicitly when one candidate list is exhausted.

                # INNER_LOOP: Aim for length_sequence successfully executed actions.
                # Stop after max_failures consecutive attempts with status 'execution_failed' (i.e. timeouts, detached elements,
                # navigation during execution, or a target selector that no longer matches exactly one element.)
                # Stop when no candidate actions remain.
                while (completed < length_sequence
                       and consecutive_execution_failures < max_failures
                       and not sequence_stopped):

                    # DERIVE_ACTIONS: Ask the configured steps for the current possible actions.
                    possible_actions = steps.derive_actions()

                    remaining_actions = list(possible_actions) # Remove skipped targets from this copy.

                    # SELECT and EXECUTE ACTION
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
                        # No actions were derived, or every target was skipped. Stop without an execution failure.
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
                        oracle_checks += steps.check_oracles(oracle_findings, run_cnt, attempts)

                # Stop the sequence when no reachable candidate remains or after max_failures consecutive failed attempts.
                if consecutive_execution_failures >= max_failures:
                    reason = print_sequence_stop(run_cnt, f"{max_failures} consecutive failed attempts.")
                    sequence_stops.append(reason)

                # Record the actual counts for this sequence.
                sequence_results.append({
                    'sequence': run_cnt, 'completed': completed, 'attempts': attempts,
                    'oracle_checks': oracle_checks,
                    'oracle_findings': len(oracle_findings) - findings_before_sequence,
                })
            finally:
                # Also runs for discovery, execution, oracle errors and Ctrl+C.
                steps.end_sequence()
    finally:
        steps.end_test()

    steps.report_test(url, num_runs, length_sequence, oracle_findings,
                      execution_failures, sequence_stops,
                      sequence_results=sequence_results)
