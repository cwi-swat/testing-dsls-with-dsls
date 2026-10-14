"""Checks for generic block timings, independent of a browser."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'testar'))
from performance import PerformanceMeasurements
from reporting import print_performance_phase, print_performance_summary


class PerformanceTests(unittest.TestCase):
    def test_reset_one_phase_preserves_other_phases(self):
        timings = PerformanceMeasurements(True)
        with patch('performance.perf_counter', side_effect=[0, 1, 2, 3, 4, 5]):
            timings.call('discovery', 'snapshot', lambda: None)
            timings.call('descriptions', 'snapshot', lambda: None)
            with timings.measure('discovery'):
                pass
        timings.reset('discovery')
        self.assertEqual(set(timings.measurements), {'descriptions.snapshot'})
        self.assertEqual(timings.breakdown('discovery'), {})

    def test_exception_still_records_elapsed_time(self):
        timings = PerformanceMeasurements(True)
        with patch('performance.perf_counter', side_effect=[10.0, 10.25]):
            with self.assertRaises(ValueError):
                with timings.measure('my_custom_phase'):
                    raise ValueError('test')
        self.assertEqual(timings.measurements['my_custom_phase']['seconds'], 0.25)

    def test_reporting_does_not_start_a_timer(self):
        timings = PerformanceMeasurements(True)
        timings.measurements['my_custom_phase'] = {'seconds': 0.25, 'calls': 1}
        output = io.StringIO()
        with patch('performance.perf_counter', side_effect=AssertionError('report started timer')):
            with contextlib.redirect_stdout(output):
                print_performance_summary(timings, 'test')
        self.assertIn('my_custom_phase: 0.250s', output.getvalue())

    def test_core_and_backend_operations_share_one_storage(self):
        timings = PerformanceMeasurements(True)
        with patch('performance.perf_counter', side_effect=[1.0, 1.1, 1.2, 1.5]):
            with timings.measure('discovery'):
                timings.call('discovery', 'snapshot', lambda: None)
        self.assertAlmostEqual(timings.measurements['discovery']['seconds'], 0.5)
        self.assertAlmostEqual(timings.breakdown('discovery')['snapshot']['seconds'], 0.1)
        timings.reset()
        self.assertEqual(timings.measurements, {})

    def test_disabled_measurements_run_code_without_clock_or_output(self):
        timings = PerformanceMeasurements(False)
        operation = Mock()
        output = io.StringIO()
        with patch('performance.perf_counter', side_effect=AssertionError('clock used')):
            with contextlib.redirect_stdout(output):
                with timings.measure('anything'):
                    operation()
                print_performance_phase(timings, 'anything')
                print_performance_summary(timings)
        operation.assert_called_once()
        self.assertEqual(timings.measurements, {})
        self.assertEqual(output.getvalue(), '')
