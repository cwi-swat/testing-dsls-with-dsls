"""Measure TESTAR steps without putting timing administration in the test loop."""
from time import perf_counter

from performance import PerformanceMeasurements
from reporting import print_performance_summary, print_sequence_summary


class PerformanceTESTARSteps:
    """Wrap the TESTAR steps and collect their times and report counts.

    Call begin_test and end_test around the test to measure its complete duration.
    Sequence totals include startup, preparations, step reporting and cleanup.
    The final test report runs after end_test and is outside the total timer.
    With detailed=True, also collect and print durations for individual steps.
    With detailed=False, this wrapper still measures test and sequence totals.
    """

    def __init__(self, steps, *, detailed=False):
        self.steps = steps
        self.detailed = detailed
        self.sequence_measurements = []
        self.total_seconds = None
        self._step_started = None

    @property
    def session(self):
        """Expose the wrapped session for other wrappers that need browser access."""
        return getattr(self.steps, 'session', None)

    def begin_test(self):
        """Start measuring the complete test, before opening its first browser."""
        self.sequence_measurements = []
        self.total_seconds = None
        self._test_started = perf_counter()
        self.steps.begin_test()

    def end_test(self):
        """Stop the total timer, also when the test was interrupted or failed."""
        try:
            self.steps.end_test()
        finally:
            self.total_seconds = perf_counter() - self._test_started

    def begin_sequence(self, url):
        """Start a sequence timer and measure opening and preparing its session."""
        self._sequence_started = perf_counter()
        self._sequence_number = len(self.sequence_measurements) + 1
        self._sequence_counts = dict(completed=0, attempts=0, oracle_checks=0, oracle_findings=0)
        self._sequence_phases = {}
        self._step_started = None
        self._sequence_failed = False
        self._timings = PerformanceMeasurements(self.detailed)
        with self._timings.measure('startup'):
            self.steps.begin_sequence(url)
        self._add_phases()

    def derive_actions(self):
        """Start a derivation step and count the actions returned by the backend.

        The duration includes discovery, descriptions and any backend retries.
        Read the optional element count without making another browser call.
        """
        # A step without oracle checks (such as all targets skipped) ends here
        # or at end_sequence. Never derive extra actions just for measurements.
        self._finish_step()
        self._timings.reset()
        self._step_started = perf_counter()
        self._step_counts = dict(elements='unknown', possible_actions=0, completed=0,
                                 attempts=0, oracle_checks=0, oracle_findings=0)
        self._first_attempt = self._sequence_counts['attempts'] + 1
        actions = self._call('derive_actions', self.steps.derive_actions)
        count = getattr(self.session, 'actionable_element_count', None)
        self._step_counts['elements'] = count if count is not None else 'unknown'
        self._step_counts['possible_actions'] = len(actions)
        return actions

    def select_action(self, possible_actions):
        """Measure selection and return the wrapped choice unchanged."""
        return self._call('selection', self.steps.select_action, possible_actions)

    def execute_action(self, action, value=None):
        """Measure one attempt, including reachability, and count its outcome."""
        self._step_counts['attempts'] += 1
        self._sequence_counts['attempts'] += 1
        if value is None:
            result = self._call('execution', self.steps.execute_action, action)
        else:
            result = self._call('execution', self.steps.execute_action, action, value=value)
        if result.status == 'execution_succeeded':
            self._step_counts['completed'] += 1
            self._sequence_counts['completed'] += 1
        return result

    def check_oracles(self, findings, sequence, attempt):
        """Measure oracle calls, count new findings and report this derivation step.

        Oracle checks count function calls, not assertions inside each function.
        """
        before = len(findings)
        checked = self._call('oracles', self.steps.check_oracles, findings, sequence, attempt)
        found = len(findings) - before
        self._step_counts['oracle_checks'] += checked
        self._step_counts['oracle_findings'] += found
        self._sequence_counts['oracle_checks'] += checked
        self._sequence_counts['oracle_findings'] += found
        self._finish_step()
        return checked

    def end_sequence(self):
        """Finish pending step reporting, close the session and record its total."""
        # Cleanup must still run if reporting a step fails.
        try:
            self._finish_step()
        finally:
            try:
                self._timings.reset()
                with self._timings.measure('cleanup'):
                    self.steps.end_sequence()
            finally:
                self._add_phases()
        seconds = perf_counter() - self._sequence_started
        measurements = dict(phases=dict(self._sequence_phases), total_seconds=seconds)
        self.sequence_measurements.append(measurements)
        if not self._sequence_failed:
            print_sequence_summary(dict(sequence=self._sequence_number, **self._sequence_counts,
                                        **measurements), show_timings=self.detailed)

    def report_test(self, url, num_runs, length_sequence, oracle_findings,
                    execution_failures=None, sequence_stops=None, *,
                    sequence_results=None, total_seconds=None):
        """Add measured durations, then let the wrapped steps report the test.

        Copy the sequence results so reporting does not change the loop's counts.
        """
        measured_results = None
        if sequence_results is not None:
            if len(sequence_results) != len(self.sequence_measurements):
                raise ValueError('Each sequence result must have its own measurements')
            measured_results = []
            for result, measurements in zip(sequence_results, self.sequence_measurements):
                measured_results.append(dict(result, **measurements))
        if total_seconds is None:
            total_seconds = self.total_seconds
        return self.steps.report_test(
            url, num_runs, length_sequence, oracle_findings,
            execution_failures, sequence_stops,
            sequence_results=measured_results, total_seconds=total_seconds)

    def _call(self, phase, operation, *args, **kwargs):
        """Measure a delegated call and propagate errors without retrying it."""
        try:
            with self._timings.measure(phase):
                return operation(*args, **kwargs)
        except BaseException:
            self._sequence_failed = True
            raise

    def _add_phases(self):
        """Add the current batch of phase durations to the sequence totals."""
        for phase, item in self._timings.measurements.items():
            self._sequence_phases[phase] = self._sequence_phases.get(phase, 0.0) + item['seconds']

    def _finish_step(self):
        """Report one derivation and its attempts once, also without oracle calls."""
        if self._step_started is None:
            return
        seconds = perf_counter() - self._step_started
        self._step_started = None
        self._add_phases()
        attempts = self._step_counts['attempts']
        label = (f'run {self._sequence_number}, attempts {self._first_attempt}-'
                 f'{self._sequence_counts["attempts"]}' if attempts else
                 f'run {self._sequence_number}, no execution attempt')
        print_performance_summary(self._timings, label, counts=self._step_counts, total_seconds=seconds)
