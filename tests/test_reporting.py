"""Reports distinguish executed actions, attempts, findings and failures."""
import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'testar'))
from reporting import print_test_summary, print_action_result
from browser_backend import ActionResult


class ReportingTests(unittest.TestCase):
    def test_summary_reports_actual_counts_and_separate_problem_categories(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_test_summary('local', 2, 10, ['wrong value'], ['timeout'], ['no actions'],
                               sequence_results=[{'sequence': 1, 'completed': 10, 'attempts': 12, 'oracle_checks': 20},
                                                 {'sequence': 2, 'completed': 3, 'attempts': 4, 'oracle_checks': 6}])
        text = output.getvalue()
        for expected in ['Target Sequence Length per Run: 10',
                         'Sequence 1: 10 completed actions, 12 execution attempts',
                         'Sequence 2: 3 completed actions, 4 execution attempts',
                         'Oracle checks: 26', 'Oracle findings: 1',
                         'Execution failures: 1', 'Early sequence stops: 1']:
            self.assertIn(expected, text)

    def test_summary_with_no_sequences_reports_zero_checks(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_test_summary('local', 0, 10, [], sequence_results=[])
        self.assertIn('Oracle checks: 0', output.getvalue())
        self.assertNotIn('Sequence 1:', output.getvalue())

    def test_action_outcomes_have_distinct_messages(self):
        for status, expected in [('execution_succeeded', 'Action 2 of 10 completed'),
                                 ('execution_skipped', 'Skipping unreachable target: #button'),
                                 ('execution_failed', 'Execution attempt 3 in sequence 1 failed')]:
            with self.subTest(status=status):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    message = print_action_result(ActionResult(status, 'timeout', 'TimeoutError'),
                                                  {'selector': '#button'}, sequence=1, attempt=3,
                                                  action_number=2, length_sequence=10)
                self.assertIn(expected, output.getvalue())
                if status == 'execution_failed':
                    self.assertEqual(message, output.getvalue().strip())
                else:
                    self.assertIsNone(message)
