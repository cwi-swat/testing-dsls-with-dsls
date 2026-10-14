"""Check all three input modes through action descriptions."""
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'testar'))
from browser_test_support import open_session


class InputModesTests(unittest.TestCase):
    def type_text(self, session, element, value, mode):
        """Use a derived action so input tests cover the same route as the explorer."""
        action = next(action for action in session.derive_action_descriptions([element])
                      if action['kind'] == 'type_text'
                      and action['parameters']['mode'] == mode)
        result = session.execute_action_description(action, value=value)
        self.assertEqual(result.status, 'execution_succeeded', result.error)

    def test_invalid_number_input_is_attempted(self):
        session = open_session(self)
        page = session.page
        page.set_content('<input id="number" type="number" value="123">')
        element = page.locator('#number')
        self.type_text(session, element, '-', 'replace')
        self.assertEqual(element.input_value(), '')
        self.type_text(session, element, '42', 'replace')
        self.assertEqual(element.input_value(), '42')

    def test_number_modes_ignore_cursor_position(self):
        session = open_session(self)
        session.page.set_content('<input id="number" type="number" value="5">')
        element = session.page.locator('#number')
        for mode, expected in [('append', '569'), ('prepend', '695'), ('replace', '69')]:
            for initial_key in ['Home', 'End']:
                with self.subTest(mode=mode, cursor=initial_key):
                    element.fill('5')
                    element.press(initial_key)
                    self.type_text(session, element, '69', mode)
                    self.assertEqual(element.input_value(), expected)

    def test_invalid_parameters_preserve_input(self):
        session = open_session(self)
        session.page.set_content('<input id="text" value="original">')
        element = session.page.locator('#text')
        description = next(d for d in session.derive_action_descriptions([element])
                           if d['kind'] == 'type_text')
        for changes, value in [({'mode': 'unknown'}, '42'),
                               ({'submit_key': 'Escape'}, '42'),
                               ({'input_strategy': 'unknown'}, None),
                               ({}, 42)]:
            with self.subTest(changes=changes, value=value):
                invalid = {**description, 'parameters': {**description['parameters'], **changes}}
                with self.assertRaises(ValueError):
                    session.execute_action_description(invalid, value=value)
                self.assertEqual(element.input_value(), 'original')

    def test_selected_strategy_generates_input_only_at_execution(self):
        session = open_session(self)
        session.page.set_content('<input id="text">')
        element = session.page.locator('#text')
        with patch('playwright_backend.generate_random_text', return_value='letters') as text:
            with patch('playwright_backend.generate_random_number', return_value='42') as number:
                with patch('playwright_backend.generate_naughty_string', return_value='odd') as naughty:
                    actions = session.derive_actions([])
                    text.assert_not_called()
                    number.assert_not_called()
                    naughty.assert_not_called()
                    action = next(a for a in actions if a['kind'] == 'type_text'
                                  and a['parameters']['input_strategy'] == 'random_number'
                                  and a['parameters']['mode'] == 'replace')
                    result = session.execute_action_description(action)
                    self.assertEqual(result.status, 'execution_succeeded', result.error)
                    self.assertEqual(element.input_value(), '42')
                    number.assert_called_once_with()
                    text.assert_not_called()
                    naughty.assert_not_called()
                    # A caller-supplied value must bypass the generator.
                    session.execute_action_description(action, value='shared')
                    self.assertEqual(element.input_value(), 'shared')
                    number.assert_called_once_with()

    def test_each_input_strategy_uses_its_own_generator(self):
        session = open_session(self)
        session.page.set_content('<input>')
        actions = session.derive_actions([])
        for strategy, generator, value in [
            ('random_text', 'generate_random_text', 'letters'),
            ('random_number', 'generate_random_number', '42'),
            ('naughty_string', 'generate_naughty_string', '<odd>'),
        ]:
            with self.subTest(strategy=strategy):
                action = next(a for a in actions if a['kind'] == 'type_text'
                              and a['parameters']['input_strategy'] == strategy
                              and a['parameters']['mode'] == 'replace')
                with patch('playwright_backend.' + generator, return_value=value) as generate:
                    result = session.execute_action_description(action)
                self.assertEqual(result.status, 'execution_succeeded', result.error)
                self.assertEqual(session.page.locator('input').input_value(), value)
                generate.assert_called_once_with()

    def test_input_modes_through_descriptions(self):
        session = open_session(self)
        page = session.page
        page.set_content('<input id="text" type="text" value="old">')
        element = page.locator('#text')
        descriptions = session.derive_action_descriptions([element])
        self.assertEqual(len(descriptions), 12)
        for strategy in ['random_text', 'random_number', 'naughty_string']:
            for mode in ['append', 'prepend', 'replace']:
                description = next(d for d in descriptions if d['kind'] == 'type_text'
                                   and d['parameters']['input_strategy'] == strategy
                                   and d['parameters']['mode'] == mode)
                element.fill('old')
                element.press('Home')
                result = session.execute_action_description(description, value='42')
                self.assertEqual(result.status, 'execution_succeeded', result.error)
                self.assertEqual(element.input_value(), {'append': 'old42', 'prepend': '42old', 'replace': '42'}[mode])
        replace = next(d for d in descriptions if d['kind'] == 'type_text'
                       and d['parameters']['mode'] == 'replace')
        session.execute_action_description(replace, value='')
        self.assertEqual(element.input_value(), '')
