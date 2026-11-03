"""Compare native TESTAR steps with evidence-recording steps on identical local work."""
from argparse import ArgumentParser
from contextlib import contextmanager, redirect_stdout
from datetime import datetime
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
import json
from pathlib import Path
import platform
from statistics import median
import sys
from threading import Thread
from unittest.mock import patch
from uuid import uuid4

from playwright.sync_api import sync_playwright as native_playwright
from testar_evidence import EvidenceReader
from testar_evidence_playwright import CaptureOptions, sync_playwright as recording_playwright

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src/testar"))
from TESTAR_steps import TESTARSteps
from performance_steps import PerformanceTESTARSteps
from playwright_backend import PlaywrightSession
from recording_steps import RecordingTESTARSteps


class BenchmarkBackend:
    """Use the same browser setup and real miniTESTAR session for both modes."""
    def __init__(self, recording, directory, settings):
        self.recording = recording
        self.directory = directory
        self.settings = settings
        self.browser_version = None

    def start(self, url):
        if self.recording:
            manager = recording_playwright(evidence_path=self.directory,
                capture_options=CaptureOptions(screenshots=not self.settings.no_screenshots))
        else:
            manager = native_playwright()
        runtime = manager.start()
        browser = None
        try:
            options = {"headless": True}
            if self.settings.channel:
                options["channel"] = self.settings.channel
            browser = runtime.chromium.launch(**options)
            self.browser_version = browser.version
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()
            page.set_default_timeout(5_000)
            page.goto(url)
            return PlaywrightSession(page, context, browser, runtime)
        except BaseException:
            try:
                if browser is not None:
                    browser.close()
            finally:
                runtime.stop()
            raise


@contextmanager
def local_page(settings):
    document = Path(__file__).with_name("recording_fixture.html").read_text(encoding="utf-8")
    widgets = "".join(f'<div id="widget-{index}" title="Item {index}" data-index="{index}">Item {index}</div>'
                      for index in range(settings.widgets))
    buttons = "".join(f'<button type="button" id="extra-{index}">Alternative {index}</button>'
                      for index in range(settings.extra_buttons))
    content = document.replace("{{widgets}}", widgets).replace("{{buttons}}", buttons).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, format, *arguments):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def planned_action(index):
    cycle = index // 5
    return (
        ("amount", "type_text", {"mode": "replace", "input_strategy": "random_text"}, f"value-{cycle}"),
        ("plan", "select_option", {"label": "Premium"}, None),
        ("apply", "click", {}, None),
        ("amount", "press_key", {"key": "ArrowUp"}, None),
        ("clear", "click", {}, None),
    )[index % 5]


def validate_trace(directory, action_count):
    traces = list(directory.glob("*/manifest.json"))
    if len(traces) != 1:
        raise AssertionError("Recording must produce exactly one trace")
    trace = EvidenceReader.read(traces[0].parent)
    expected_executions = 1 + action_count
    assert len(trace.action_executions) == expected_executions
    assert len(trace.recorded_transitions) == expected_executions
    assert len(trace.observations) == expected_executions + 1
    assert len(trace.oracle_results) == action_count
    assert all(result["oracle_status"] == "passed" for result in trace.oracle_results)
    assert all(execution["status"] == "completed" for execution in trace.action_executions.values())
    assert sum(observation["available_action_scope"] == "eligible"
               for observation in trace.observations.values()) == action_count
    operation_reports = []
    for observation in trace.observations.values():
        for artifact in observation["artifacts"]:
            if artifact["media_type"] == "application/json":
                operation_reports.append(json.loads((traces[0].parent / artifact["path"]).read_text(encoding="utf-8")))
    assert len(operation_reports) == sum(index % 5 == 0 for index in range(action_count))
    for report in operation_reports:
        assert report["format"] == "compound-action-operations" and report["version"] == 1
        assert report["action_execution"] in trace.action_executions
        assert [operation["method"] for operation in report["operations"]] == [
            "Locator.fill", "Locator.press_sequentially", "Locator.press"]
        assert all(operation["outcome"] == "returned" for operation in report["operations"])
    return {"observations": len(trace.observations), "action_executions": expected_executions,
            "oracle_results": len(trace.oracle_results),
            "compound_actions": len(operation_reports),
            "atomic_operations": sum(len(report["operations"]) for report in operation_reports),
            "trace_bytes": sum(path.stat().st_size for path in traces[0].parent.rglob("*") if path.is_file())}


def run_sample(mode, directory, settings, url):
    directory.mkdir()
    backend = BenchmarkBackend(mode == "recording", directory / "evidence", settings)
    expected = {"value": "", "plan": "Standard", "submissions": 0}

    def check_form(page):
        actual = page.evaluate("() => ({value: amount.value, plan: plan.value, submissions: window.submissions})")
        assert actual == expected, f"Expected {expected}, obtained {actual}"

    steps = TESTARSteps(backend=backend, oracles=[check_form])
    if mode == "recording":
        steps = RecordingTESTARSteps(steps)
    steps = PerformanceTESTARSteps(steps, detailed=True)
    findings = []
    workload = []
    with (directory / "steps.txt").open("w", encoding="utf-8") as output, redirect_stdout(output):
        steps.begin_test()
        try:
            steps.begin_sequence(url)
            for index in range(settings.actions):
                descriptions = steps.derive_actions()
                target, kind, parameters, value = planned_action(index)
                selected_index = next(position for position, action in enumerate(descriptions)
                    if action["target"]["id"] == target and action["kind"] == kind
                    and all(action["parameters"].get(key) == item for key, item in parameters.items()))
                # Keep the full available-action list; only replace the random choice.
                with patch("TESTAR_steps.random.randint", return_value=selected_index):
                    action = steps.select_action(descriptions)
                workload.append({"available": [(item["target"]["id"], item["kind"], item["parameters"])
                                               for item in descriptions], "selected": selected_index, "value": value})
                result = steps.execute_action(action, value=value)
                if result.status != "execution_succeeded":
                    raise AssertionError(f"Action {index + 1}: {result}")
                if kind == "type_text":
                    expected["value"] = value
                    expected["submissions"] += 1
                elif kind == "select_option":
                    expected["plan"] = "Premium"
                elif target == "apply":
                    expected["submissions"] += 1
                elif target == "clear":
                    expected.update(value="", plan="Standard")
                assert steps.check_oracles(findings, 1, index + 1) == 1
                if findings:
                    raise AssertionError(f"Oracle failed after action {index + 1}: {findings}")
        finally:
            try:
                steps.end_sequence()
            finally:
                steps.end_test()
    result = {"mode": mode, "browser_version": backend.browser_version,
              "seconds": steps.total_seconds, "phases": steps.sequence_measurements[0]["phases"],
              "workload_sha256": sha256(json.dumps(workload, sort_keys=True).encode()).hexdigest()}
    # Reconstruct evidence and verify screenshots after stopping the benchmark timers.
    if mode == "recording":
        result["evidence"] = validate_trace(directory / "evidence", settings.actions)
    elif (directory / "evidence").exists():
        raise AssertionError("Default mode must use native Playwright without recording")
    return result


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise ValueError("Use a positive integer")
    return number


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--actions", type=positive_integer, default=20)
    parser.add_argument("--repeats", type=positive_integer, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--widgets", type=positive_integer, default=100)
    parser.add_argument("--extra-buttons", type=positive_integer, default=10)
    parser.add_argument("--channel", default="", help="Browser channel, e.g. chrome; omitted uses bundled Chromium")
    parser.add_argument("--no-screenshots", action="store_true")
    settings = parser.parse_args()
    if settings.warmups < 0:
        parser.error("--warmups must be zero or greater")
    directory = REPOSITORY / "target/benchmarks" / (datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "-" + uuid4().hex[:8])
    directory.mkdir(parents=True)
    report = {"settings": vars(settings), "python": platform.python_version(), "platform": platform.platform(),
              "packages": {name: version(name) for name in ("playwright", "testar-evidence", "testar-evidence-playwright-adapter")},
              "samples": []}
    with local_page(settings) as url:
        for pair_index in range(settings.warmups + settings.repeats):
            warmup = pair_index < settings.warmups
            order = ("default", "recording") if pair_index % 2 == 0 else ("recording", "default")
            pair = []
            for mode in order:
                sample = run_sample(mode, directory / f"pair-{pair_index + 1}-{mode}", settings, url)
                sample.update(pair=pair_index + 1, warmup=warmup)
                pair.append(sample)
                report["samples"].append(sample)
                (directory / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                print(f'{"Warm-up" if warmup else "Measured"} pair {pair_index + 1}, {mode}: {sample["seconds"]:.3f}s', flush=True)
            assert pair[0]["workload_sha256"] == pair[1]["workload_sha256"], "Modes received different workloads"
    measured = [sample for sample in report["samples"] if not sample["warmup"]]
    summary = {mode: {phase: median(sample["seconds"] if phase == "total" else sample["phases"].get(phase, 0)
                    for sample in measured if sample["mode"] == mode)
                    for phase in ("startup", "derive_actions", "selection", "execution", "oracles", "cleanup", "total")}
               for mode in ("default", "recording")}
    report["median_seconds"] = summary
    (directory / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nMedian seconds             Default   Recording       Extra")
    for phase in summary["default"]:
        baseline, recording = summary["default"][phase], summary["recording"][phase]
        print(f"{phase:24} {baseline:9.3f} {recording:11.3f} {recording - baseline:11.3f}")
    print(f'\nRecording/default total: {summary["recording"]["total"] / summary["default"]["total"]:.2f}x')
    print(f"Results and traces: {directory}")


if __name__ == "__main__":
    main()
