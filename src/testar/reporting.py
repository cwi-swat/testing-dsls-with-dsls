"""Format and print attempted actions, timings and test results."""


def format_element_info(info):
    return (
        f"Tag: {info['tag_name']}, ID: {info['id']}, Class: {info['class']}, Type: {info['type']}, "
        f"Text: {info['text']}, Location: {info['location']}, Size: {info['size']}, "
        f"Attributes: {info['attributes']}"
    )


def log_info(action, element_info, *args):
    """Print just before attempting an action; this does not confirm success."""
    info = format_element_info(element_info)
    if args:
        print(f"{action} on {info} with {args}")
    else:
        print(f"{action} on {info}")


def print_derivation_retry(attempt, max_attempts):
    print('Could not derive actions; '
          f'trying again (attempt {attempt} of {max_attempts}).', flush=True)


def print_sequence_start(sequence, num_runs):
    print(f"Starting test sequence number {sequence} of {num_runs}")


def print_sequence_stop(sequence, reason):
    message = f"Sequence {sequence} stopped: {reason}"
    print(message)
    return message


def print_action_result(result, description, *, sequence=None, attempt=None,
                        action_number=None, length_sequence=None):
    """Print an execution result; return the failure message for the core to record."""
    if result.status == 'execution_succeeded':
        print('Action executed' if action_number is None
              else f"Action {action_number} of {length_sequence} completed")
    elif result.status == 'execution_skipped':
        print(f"Skipping unreachable target: {description['selector']}")
    elif result.status == 'execution_failed':
        context = (f"Execution attempt {attempt} in sequence {sequence}"
                   if sequence is not None else 'Execution attempt')
        message = f"{context} failed ({result.error_type}): {result.error}"
        print(message)
        return message
    else:
        raise ValueError('Unknown action result: ' + str(result.status))
    return None


def print_oracle_finding(name, error, sequence, attempt):
    message = f"{name} detected that {error} in sequence {sequence} and attempt {attempt}"
    print(message)
    return message


def print_oracle_error(name, error):
    print(f"An unexpected error occurred in oracle {name}: {error}")


def print_test_summary(url, num_runs, length_sequence, oracle_findings,
                       execution_failures=None, sequence_stops=None, *, sequence_results=None):
    """Report SUT oracle findings separately from execution problems and stops.

    Counts describe recorded findings, not proof of correctness. With no
    oracles, zero oracle findings simply means no properties were checked.
    Show the configured sequence length and the actual counts supplied by the core.
    """
    execution_failures = execution_failures or []
    sequence_stops = sequence_stops or []
    print("=" * 30)
    print("TEST SUMMARY REPORT")
    print("=" * 30)
    print(f"Tested URL: {url}")
    print(f"Number of Runs: {num_runs}")
    print(f"Target Sequence Length per Run: {length_sequence}")
    for result in sequence_results or []:
        print(f"Sequence {result['sequence']}: {result['completed']} completed actions, "
              f"{result['attempts']} execution attempts, "
              f"{result.get('oracle_checks', 0)} oracle checks")
    if sequence_results is not None:
        print(f"Oracle checks: {sum(result.get('oracle_checks', 0) for result in sequence_results)}")
    for title, messages in [
        ('Oracle findings', oracle_findings),
        ('Execution failures', execution_failures),
        ('Early sequence stops', sequence_stops),
    ]:
        print(f"{title}: {len(messages)}")
        for message in messages:
            print(f"  {message}")
    print("=" * 30)


def print_performance_phase(performance, phase, description=''):
    """Print a finished phase; names and description are supplied by the caller."""
    if not performance.enabled:
        return
    seconds = performance.measurements[phase]['seconds']
    print(f'{phase.upper()}: {description} in {seconds:.3f}s', flush=True)
    for name, item in performance.breakdown(phase).items():
        seconds, calls = item['seconds'], item['calls']
        average_ms = seconds * 1000 / calls if calls else 0
        print(f'  {phase}.{name}: {seconds:.3f}s / {calls} calls '
              f'({average_ms:.3f} ms/call)', flush=True)


def print_performance_summary(performance, description=''):
    """Print stored phase totals and details without starting or stopping timers."""
    if not performance.enabled:
        return
    parts = []
    for phase, item in performance.measurements.items():
        # Dotted names describe operations inside a phase, not phase totals.
        if '.' in phase:
            continue
        details = ', '.join(
            f"{name}: {detail['seconds']:.3f}s / {detail['calls']} calls"
            for name, detail in performance.breakdown(phase).items())
        suffix = f' ({details})' if details else ''
        parts.append(f"{phase}: {item['seconds']:.3f}s{suffix}")
    print(f"TIMING {description}: " + ' | '.join(parts), flush=True)
