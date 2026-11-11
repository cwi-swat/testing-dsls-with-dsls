"""Check timing accounting and restoration without performance thresholds."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from timing_breakdown import TimingBreakdown


class TimingBreakdownTests(unittest.TestCase):
    def test_nested_self_times_account_for_the_phase_without_double_counting(self):
        ticks = iter((0, 1, 2, 3, 4, 5))
        timings = TimingBreakdown(True, clock=lambda: next(ticks))
        result = timings.call("execution", lambda: timings.measure("outer", lambda:
            timings.measure("inner", lambda: "result")))
        self.assertEqual("result", result)
        rows = {row["operation"]: row for row in timings.summary()}
        self.assertEqual(5, rows["phase_total"]["total_seconds"])
        self.assertEqual(2, rows["phase_total"]["self_seconds"])
        self.assertEqual(3, rows["outer"]["total_seconds"])
        self.assertEqual(2, rows["outer"]["self_seconds"])
        self.assertEqual(1, rows["inner"]["self_seconds"])
        self.assertEqual(5, sum(row["self_seconds"] for row in rows.values()))

    def test_disabled_timings_leave_functions_untouched_and_do_not_read_clock(self):
        from playwright.sync_api import Page
        from testar_evidence import storage
        original_evaluate, original_write = Page.evaluate, storage._write_all
        def unexpected_clock():
            raise AssertionError("Disabled timings must not read the clock")
        with TimingBreakdown(clock=unexpected_clock) as timings:
            self.assertIs(original_evaluate, Page.evaluate)
            self.assertIs(original_write, storage._write_all)
            self.assertEqual(12, timings.call("execution", lambda: 12))
        self.assertEqual([], timings.summary())

    def test_failed_operation_preserves_exception_restores_patches_and_excludes_later_work(self):
        from playwright.sync_api import Page
        from testar_evidence import codec, storage
        original_evaluate, original_write = Page.evaluate, storage._write_all
        failure = ValueError("Original failure")
        def fail():
            raise failure
        with self.assertRaises(ValueError) as raised:
            with TimingBreakdown(True) as timings:
                self.assertIsNot(original_evaluate, Page.evaluate)
                with self.assertRaises(ValueError):
                    timings.call("execution", fail)
                before = timings.summary()
                codec.to_data({"outside_phase": True})
                self.assertEqual(before, timings.summary())
                raise failure
        self.assertIs(failure, raised.exception)
        self.assertIs(original_evaluate, Page.evaluate)
        self.assertIs(original_write, storage._write_all)
        self.assertEqual(1, timings.summary()[0]["errors"])

    def test_file_wrappers_delegate_real_writes_and_keep_sync_enabled(self):
        from testar_evidence import storage
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "event.jsonl"
            with patch.object(storage.os, "fsync") as sync:
                with TimingBreakdown(True) as timings:
                    with path.open("wb") as output:
                        timings.call("execution", storage._write_all, output, b"evidence\n")
                    self.assertEqual(b"evidence\n", path.read_bytes())
                sync.assert_called_once()
        rows = {row["operation"]: row for row in timings.summary()}
        self.assertEqual(1, rows["file_write"]["calls"])
        self.assertEqual(9, rows["file_write"]["bytes"])
        self.assertEqual(1, rows["file_flush"]["calls"])
        self.assertEqual(1, rows["disk_sync"]["calls"])


class DomCaptureDiagnosticsTests(unittest.TestCase):
    def test_changed_capture_script_is_rejected_instead_of_reporting_misleading_timings(self):
        from dom_capture_diagnostics import instrument_capture
        with self.assertRaisesRegex(RuntimeError, "Capture script changed"):
            instrument_capture("(options) => ({nodes: []})")

    @unittest.skipUnless(os.environ.get("TESTAR_BROWSER_TESTS") == "1", "Opt-in browser diagnostic check")
    def test_browser_diagnostics_preserve_capture_data_and_wrappers_strip_diagnostics(self):
        from playwright.sync_api import sync_playwright, Page
        from testar_evidence_playwright.capture import _resource
        from dom_capture_diagnostics import instrument_capture
        options = {"excludedAttributes": ["data-excluded"], "computedStyles": ["display", "color"],
                   "maxValueCharacters": 1000, "maxTotalCharacters": 100000,
                   "maxAttributesPerWidget": 256, "maxWidgets": 100}
        original_evaluate = Page.evaluate
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel=os.environ.get("TESTAR_BROWSER_CHANNEL", "chrome"))
            try:
                page = browser.new_page()
                page.set_content('<title>Fixture</title><input type="password" value="secret">'
                                 '<input value="\u00e9quipe"><div hidden>Hidden</div><div id="host"></div>')
                page.evaluate("document.querySelector('#host').attachShadow({mode: 'open'}).innerHTML = '<button>Shadow</button>'")
                script = _resource("capture.js")
                for limit in (100, 4):
                    options["maxWidgets"] = limit
                    expected = page.evaluate(script, options)
                    result = page.evaluate(instrument_capture(script), options)
                    self.assertEqual(expected, result["capture"])
                    diagnostics = result["diagnostics"]
                    self.assertEqual(len(expected["nodes"]), diagnostics["widget_count"])
                    self.assertEqual(len(json.dumps(expected, ensure_ascii=False, separators=(",", ":")).encode()),
                                     diagnostics["json_bytes"])
                    self.assertGreaterEqual(diagnostics["browser_millis"], diagnostics["property_read_millis"])
                    self.assertGreaterEqual(diagnostics["property_read_millis"] + 0.01,
                                            sum(diagnostics["property_stages_millis"].values()))
                    json_result = page.evaluate(instrument_capture(script, json_transport=True), options)
                    self.assertIsInstance(json_result["capture"], str)
                    self.assertEqual(expected, json.loads(json_result["capture"]))
                    self.assertEqual("json", json_result["diagnostics"]["transport"])
                    with TimingBreakdown(True) as timings:
                        actual = timings.call("execution", page.evaluate, script, options)
                        self.assertEqual(expected, actual)
                        page.evaluate(script, options)
                        self.assertEqual(1, len(timings.dom_captures))
                        self.assertEqual("execution", timings.dom_captures[0]["phase"])
                    from testar_evidence_playwright.capture import _capture_script, capture_page, CaptureOptions
                    with TimingBreakdown(True) as timings:
                        actual = timings.call("execution", page.evaluate, _capture_script(), options)
                        self.assertIsInstance(actual, str)
                        self.assertEqual(expected, json.loads(actual))
                        self.assertEqual("json", timings.dom_captures[0]["transport"])
                        timings.call("execution", capture_page, page, CaptureOptions(screenshots=False))
                        decoding = [row for row in timings.summary() if row["operation"] == "dom_json_decode"]
                        self.assertEqual(1, decoding[0]["calls"])
                    self.assertIs(original_evaluate, Page.evaluate)
            finally:
                browser.close()
