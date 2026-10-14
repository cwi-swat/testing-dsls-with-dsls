"""Generated oracle loading: valid modules and recoverable loading errors."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'testar'))
import testingQLprograms as ql


class OracleLoadingTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.html = Path(folder.name) / 'example.html'

    def test_valid_oracles_are_loaded_and_helpers_are_ignored(self):
        self.html.with_suffix('.py').write_text(
            'def first_oracle(page): page.append("first")\n'
            'def helper(page): raise AssertionError("helper called")\n'
            'not_callable_oracle = 42\n'
            'def second_oracle(page): page.append("second")\n')
        oracles = ql.load_oracles(self.html)
        observed = []
        for oracle in oracles:
            oracle(observed)
        self.assertEqual(observed, ['first', 'second'])

    def test_missing_file_or_no_functions_returns_empty_list_with_message(self):
        for content in [None, 'answer = 42\n']:
            with self.subTest(content=content):
                if content is not None:
                    self.html.with_suffix('.py').write_text(content)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(ql.load_oracles(self.html), [])
                self.assertIn('Running without oracles', output.getvalue())

    def test_syntax_and_import_errors_return_empty_list_with_reason(self):
        for content, error_type in [('def broken(', 'SyntaxError'),
                                    ('raise RuntimeError("broken import")', 'RuntimeError')]:
            with self.subTest(error_type=error_type):
                self.html.with_suffix('.py').write_text(content)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(ql.load_oracles(self.html), [])
                self.assertIn(error_type, output.getvalue())
                self.assertIn('Running without oracles', output.getvalue())

    def test_loaded_oracle_is_passed_to_explorer(self):
        self.html.with_suffix('.py').write_text('def example_oracle(page): pass\n')
        with patch.object(ql, 'testar') as run:
            ql.testar_QL_webApp(str(self.html))
        self.assertEqual(run.call_args.args[0], self.html.resolve().as_uri())
        self.assertEqual([oracle.__name__ for oracle in run.call_args.args[5]], ['example_oracle'])
