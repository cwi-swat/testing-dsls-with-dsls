"""One optional recorder shared by the TESTAR core and browser session.

Names come from the caller, such as discovery or discovery.candidate_snapshot.
Nested durations overlap: do not add a phase total to its individual details.
Printing belongs to reporting.py, not to this recorder.
"""
from contextlib import contextmanager
from time import perf_counter


class PerformanceMeasurements:
    """Measure blocks and operations with the same timer and storage.

    When enabled is False, measured code still runs normally, but no clock
    is read and no durations are stored. Exceptions always propagate.
    """

    def __init__(self, enabled=False):
        self.enabled = enabled
        self.measurements = {}

    @contextmanager
    def measure(self, name):
        """Record elapsed time when leaving the block, even after an exception."""
        if not self.enabled:
            yield
            return
        started = perf_counter()
        try:
            yield
        finally:
            item = self.measurements.setdefault(name, {'seconds': 0.0, 'calls': 0})
            item['seconds'] += perf_counter() - started
            item['calls'] += 1

    def call(self, phase, name, operation, *args):
        """Use the same block timer for a single named backend operation."""
        with self.measure(phase + '.' + name):
            return operation(*args)

    def reset(self, phase=None):
        """Clear all measurements, or a named phase and its details."""
        if phase is None:
            self.measurements.clear()
        else:
            for name in list(self.measurements):
                if name == phase or name.startswith(phase + '.'):
                    del self.measurements[name]

    def breakdown(self, phase):
        """Return the details for a phase, without its total duration."""
        prefix = phase + '.'
        return {name[len(prefix):]: item for name, item in self.measurements.items()
                if name.startswith(prefix)}
