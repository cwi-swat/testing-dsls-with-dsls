"""Browser-free checks for the TESTAR backend boundary."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

TESTAR_PATH = str(Path(__file__).resolve().parents[1] / 'src' / 'testar')
sys.path.insert(0, TESTAR_PATH)
import miniTESTAR
from browser_backend import ActionResult


class BackendBoundaryTests(unittest.TestCase):
    def test_each_sequence_uses_a_new_session(self):
        events = []
        sessions = []
        for index in range(3):
            session = Mock()
            session.page = object()
            session.performance = None
            session.actionable_element_count = 1
            session.derive_actions.return_value = [{'kind': 'click', 'selector': '#button'}]
            session.execute_action_description.return_value = ActionResult('execution_succeeded')
            session.close.side_effect = lambda index=index: events.append(('close', index))
            sessions.append(session)
        backend = Mock()
        def start(url):
            index = sum(event[0] == 'start' for event in events)
            events.append(('start', index))
            return sessions[index]
        backend.start.side_effect = start
        prepare, oracle = Mock(), Mock()
        with contextlib.redirect_stdout(io.StringIO()):
            miniTESTAR.testar('local', 3, 1, [], [prepare], [oracle], backend=backend)
        self.assertEqual(events, [('start', 0), ('close', 0), ('start', 1), ('close', 1),
                                  ('start', 2), ('close', 2)])
        self.assertEqual([call.args[0] for call in prepare.call_args_list], [s.page for s in sessions])
        self.assertEqual([call.args[0] for call in oracle.call_args_list], [s.page for s in sessions])
        for session in sessions:
            session.execute_action_description.assert_called_once()
            session.close.assert_called_once()

    def test_empty_action_list_stops_without_execution_or_oracles(self):
        session = Mock()
        session.performance = None
        session.actionable_element_count = 0
        session.derive_actions.return_value = []
        backend = Mock()
        backend.start.return_value = session
        oracle = Mock()
        with contextlib.redirect_stdout(io.StringIO()), patch.object(miniTESTAR, 'print_test_summary') as report:
            miniTESTAR.testar('local', 1, 10, [], [], [oracle], backend=backend)
        session.execute_action_description.assert_not_called()
        oracle.assert_not_called()
        session.close.assert_called_once()
        self.assertEqual(report.call_args.kwargs['sequence_results'], [
            {'sequence': 1, 'completed': 0, 'attempts': 0, 'oracle_checks': 0}])

    def test_oracles_count_calls_and_continue_after_findings(self):
        page, findings, called = object(), [], []
        def first(received):
            self.assertIs(received, page)
            called.append('first')
            raise AssertionError('wrong value')
        def second(received):
            self.assertIs(received, page)
            called.append('second')
        with contextlib.redirect_stdout(io.StringIO()):
            checked = miniTESTAR.check_oracles(page, [first, second], findings, 2, 3)
        self.assertEqual(checked, 2)
        self.assertEqual(called, ['first', 'second'])
        self.assertEqual(len(findings), 1)
        self.assertIn('attempt 3', findings[0])
        self.assertEqual(miniTESTAR.check_oracles(page, [], findings, 2, 4), 0)

    def test_blocked_targets_are_skipped_without_extra_oracle_checks(self):
        session = Mock()
        session.performance = None
        session.actionable_element_count = 1
        blocked = {'kind': 'click', 'selector': '#blocked'}
        other = {'kind': 'press_key', 'selector': '#blocked'}
        available = {'kind': 'click', 'selector': '#available'}
        session.derive_actions.return_value = [blocked, other, available]
        session.execute_action_description.side_effect = [
            ActionResult('execution_skipped'), ActionResult('execution_succeeded')]
        backend = Mock()
        backend.start.return_value = session
        oracle = Mock()
        output = io.StringIO()
        with patch.object(miniTESTAR, 'select_action', side_effect=lambda actions: actions[0]):
            with contextlib.redirect_stdout(output):
                miniTESTAR.testar('url', 1, 1, [], [], [oracle], backend=backend)
        self.assertEqual(session.execute_action_description.call_count, 2)
        self.assertIn('Sequence 1: 1 completed actions, 2 execution attempts', output.getvalue())
        oracle.assert_called_once_with(session.page)
        session.close.assert_called_once()

    def test_all_blocked_targets_stop_the_sequence(self):
        session = Mock()
        session.performance = None
        session.actionable_element_count = 1
        session.derive_actions.return_value = [
            {'kind': 'click', 'selector': '#blocked'}]
        session.execute_action_description.return_value = ActionResult('execution_skipped')
        backend = Mock()
        backend.start.return_value = session
        oracle = Mock()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            miniTESTAR.testar('url', 1, 5, [], [], [oracle], backend=backend)
        session.execute_action_description.assert_called_once()
        oracle.assert_not_called()
        session.close.assert_called_once()
        self.assertIn('no reachable action remains', output.getvalue())
        self.assertIn('Target Sequence Length per Run: 5', output.getvalue())
        self.assertIn('Sequence 1: 0 completed actions, 1 execution attempts', output.getvalue())
        self.assertIn('Oracle checks: 0', output.getvalue())

    def test_failed_action_is_not_replayed_and_observation_is_refreshed(self):
        session = Mock()
        session.performance = None
        session.actionable_element_count = 1
        session.derive_actions.side_effect = [
            [{'selector': '#old'}], [{'selector': '#new'}]]
        session.execute_action_description.side_effect = [
            ActionResult('execution_failed', 'timeout', 'TimeoutError'), ActionResult('execution_succeeded')]
        backend = Mock()
        backend.start.return_value = session
        oracle = Mock()
        with contextlib.redirect_stdout(io.StringIO()):
            miniTESTAR.testar('url', 1, 1, [], [], [oracle], backend=backend)
        self.assertEqual(session.derive_actions.call_count, 2)
        self.assertEqual(oracle.call_count, 2)
        self.assertEqual([c.args[0]['selector'] for c in session.execute_action_description.call_args_list],
                         ['#old', '#new'])
        session.close.assert_called_once()

    def test_consecutive_failures_are_bounded(self):
        session = Mock()
        session.performance = None
        session.actionable_element_count = 1
        session.derive_actions.return_value = [{'selector': '#target'}]
        session.execute_action_description.return_value = ActionResult('execution_failed', 'timeout')
        backend = Mock()
        backend.start.return_value = session
        with contextlib.redirect_stdout(io.StringIO()):
            miniTESTAR.testar('url', 1, 1, [], [], [], backend=backend, max_failures=2)
        self.assertEqual(session.execute_action_description.call_count, 2)
        session.close.assert_called_once()

    def test_cleanup_on_preparation_discovery_execution_and_oracle_errors(self):
        for phase in ['preparation', 'discovery', 'execution', 'oracle']:
            with self.subTest(phase=phase):
                session = Mock()
                session.performance = None
                session.actionable_element_count = 1
                session.execute_action_description.return_value = ActionResult('execution_succeeded')
                session.derive_actions.return_value = [{'selector': '#target'}]
                backend = Mock()
                backend.start.return_value = session
                error = RuntimeError(phase)
                preparations = []
                if phase == 'preparation':
                    preparations = [Mock(side_effect=error)]
                elif phase == 'discovery':
                    session.derive_actions.side_effect = error
                elif phase == 'execution':
                    session.execute_action_description.side_effect = error
                with patch.object(miniTESTAR, 'check_oracles', side_effect=error if phase == 'oracle' else None):
                    with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError):
                        miniTESTAR.testar('url', 1, 1, [], preparations, [], backend=backend)
                session.close.assert_called_once()

    def test_execution_failures_are_not_oracle_findings(self):
        session = Mock()
        session.performance = None
        session.actionable_element_count = 1
        session.derive_actions.return_value = [{'selector': '#target'}]
        session.execute_action_description.return_value = ActionResult('execution_failed', 'timeout', 'TimeoutError')
        backend = Mock()
        backend.start.return_value = session
        with contextlib.redirect_stdout(io.StringIO()), patch.object(miniTESTAR, 'print_test_summary') as report:
            miniTESTAR.testar('url', 1, 1, [], [], [], backend=backend, max_failures=1)
        oracle_findings, execution_failures, sequence_stops = report.call_args.args[3:]
        self.assertEqual(oracle_findings, [])
        self.assertEqual(len(execution_failures), 1)
        self.assertEqual(len(sequence_stops), 1)

    def test_optional_timings_discover_only_once(self):
        session = Mock()
        session.performance = None
        session.actionable_element_count = 1
        session.execute_action_description.return_value = ActionResult('execution_succeeded')
        from performance import PerformanceMeasurements
        session.performance = PerformanceMeasurements()
        def discover(filters):
            session.performance.measurements['discovery.visibility'] = {'seconds': 0.02, 'calls': 1}
            return ['element']
        def describe(elements):
            session.performance.measurements['descriptions.element_info'] = {'seconds': 0.01, 'calls': 1}
            return [{'kind': 'click'}]
        def execute(description, value=None):
            session.performance.measurements['execution.reachability'] = {'seconds': 0.01, 'calls': 1}
            return ActionResult('execution_succeeded')
        def derive(filters):
            from reporting import print_performance_phase
            with session.performance.measure('discovery'):
                elements = discover(filters)
            print_performance_phase(session.performance, 'discovery', '1 elements')
            with session.performance.measure('descriptions'):
                descriptions = describe(elements)
            print_performance_phase(session.performance, 'descriptions', '1 actions')
            return descriptions
        session.derive_actions.side_effect = derive
        session.execute_action_description.side_effect = execute
        backend = Mock()
        backend.start.return_value = session
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            miniTESTAR.testar('local', 1, 1, [], [], [], backend=backend,
                             measure_timings=True)
        session.derive_actions.assert_called_once_with([])
        session.execute_action_description.assert_called_once_with({'kind': 'click'}, value=None)
        session.close.assert_called_once_with()
        self.assertTrue(session.performance.enabled)
        self.assertIn('1 elements | 1 actions', output.getvalue())
        self.assertIn('reachability:', output.getvalue())
        self.assertIn('discovery.visibility:', output.getvalue())
        self.assertIn('descriptions.element_info:', output.getvalue())

    def test_cycle_and_oracle_failures(self):
        events = []
        driver, element = object(), object()

        def prepare(received):
            self.assertIs(received, driver)
            events.append('prepare')

        def exclude(received):
            self.assertIs(received, driver)
            events.append('filter')
            return []

        def oracle(received):
            self.assertIs(received, driver)
            events.append('oracle')
            raise AssertionError('bad state')

        class Session:
            def __init__(inner):
                inner.page = driver

            def close(inner):
                events.append('close')

            def derive_actionable_elements(inner, filters):
                events.append('discover')
                for callback in filters:
                    callback(inner.page)
                return [element]

            def derive_action_descriptions(inner, elements):
                self.assertEqual(elements, [element])
                events.append('derive')
                return [{'kind': 'click', 'selector': '#fake'}]

            def derive_actions(inner, filters):
                elements = inner.derive_actionable_elements(filters)
                inner.actionable_element_count = len(elements)
                return inner.derive_action_descriptions(elements)

            def execute_action_description(inner, description, value=None):
                self.assertEqual(description['kind'], 'click')
                events.append('execute')
                return ActionResult('execution_succeeded')

        class Backend:
            def start(inner, url):
                events.append('start')
                return Session()

        with contextlib.redirect_stdout(io.StringIO()), patch.object(
            miniTESTAR, 'print_test_summary'
        ) as report:
            miniTESTAR.testar('local', 2, 2, [exclude], [prepare], [oracle],
                             backend=Backend())
        cycle = ['discover', 'filter', 'derive', 'execute', 'oracle']
        self.assertEqual(events, (['start', 'prepare'] + cycle * 2 + ['close']) * 2)
        self.assertEqual(len(report.call_args.args[3]), 4)
        self.assertEqual([r['oracle_checks'] for r in report.call_args.kwargs['sequence_results']], [2, 2])


if __name__ == '__main__':
    unittest.main()
