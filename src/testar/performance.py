"""Optional timing storage for TESTAR step wrappers."""
from contextlib import contextmanager
from time import perf_counter


class PerformanceMeasurements:
    """Accumulate elapsed seconds and call counts for named blocks.

    When enabled is False, measured code still runs normally, but no clock
    is read and no durations are stored. Exceptions always propagate.
    """

    def __init__(self, enabled=False):
        self.enabled = enabled
        self.measurements = {}

    @contextmanager
    def measure(self, name):
        """Add this block's duration and one call, even after an exception."""
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

    def reset(self):
        """Clear the measurements before the next step."""
        self.measurements.clear()
