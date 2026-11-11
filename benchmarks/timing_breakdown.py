"""Optional timing wrappers confined to one benchmark execution."""
from collections import defaultdict
from contextlib import ExitStack
from functools import wraps
from threading import local
from time import perf_counter
from unittest.mock import patch


class TimingBreakdown:
    def __init__(self, enabled=False, *, clock=perf_counter):
        self.dom_captures = []
        self.enabled = enabled
        self._clock = clock
        self._local = local()
        self._patches = ExitStack()
        self._statistics = defaultdict(lambda: {
            "calls": 0, "errors": 0, "total_seconds": 0.0, "self_seconds": 0.0,
            "max_seconds": 0.0, "bytes": 0,
        })

    def __enter__(self):
        if self.enabled:
            try:
                self._install()
            except BaseException:
                self._patches.close()
                raise
        return self

    def __exit__(self, exception_type, exception, traceback):
        self._patches.close()

    def call(self, phase, operation, *arguments, **options):
        if not self.enabled:
            return operation(*arguments, **options)
        previous = getattr(self._local, "phase", None)
        self._local.phase = phase
        try:
            return self.measure("phase_total", operation, *arguments, **options)
        finally:
            self._local.phase = previous

    def measure(self, name, operation, *arguments, **options):
        phase = getattr(self._local, "phase", None)
        if not self.enabled or phase is None:
            return operation(*arguments, **options)
        stack = getattr(self._local, "stack", None)
        if stack is None:
            stack = []
            self._local.stack = stack
        frame = {"name": name, "children": 0.0}
        stack.append(frame)
        started = self._clock()
        failed = False
        try:
            return operation(*arguments, **options)
        except BaseException:
            failed = True
            raise
        finally:
            elapsed = self._clock() - started
            stack.pop()
            statistics = self._statistics[(phase, name)]
            statistics["calls"] += 1
            statistics["errors"] += int(failed)
            statistics["total_seconds"] += elapsed
            statistics["self_seconds"] += max(0.0, elapsed - frame["children"])
            statistics["max_seconds"] = max(statistics["max_seconds"], elapsed)
            if stack:
                stack[-1]["children"] += elapsed

    def summary(self):
        return [{"phase": phase, "operation": operation, **statistics,
                 "average_millis": statistics["total_seconds"] * 1_000 / statistics["calls"]}
                for (phase, operation), statistics in sorted(self._statistics.items())]

    def _inside(self, name):
        return any(frame["name"] == name for frame in getattr(self._local, "stack", []))

    def _wrap(self, operation, name):
        @wraps(operation)
        def measured(*arguments, **options):
            label = name(*arguments, **options) if callable(name) else name
            if label is None:
                return operation(*arguments, **options)
            return self.measure(label, operation, *arguments, **options)
        return measured

    def _patch(self, owner, attribute, name, *, static=False):
        wrapped = self._wrap(getattr(owner, attribute), name)
        self._patches.enter_context(patch.object(owner, attribute, staticmethod(wrapped) if static else wrapped))

    def _install(self):
        from pathlib import Path
        from playwright import sync_api as native
        from testar_evidence import codec, records, storage
        from testar_evidence.reconstructed_evidence import ReconstructedEvidence
        from testar_evidence_playwright import capture, evidence, facade_actions

        capture_script = capture._resource("capture.js")
        from dom_capture_diagnostics import instrument_capture

        json_capture_script = capture._capture_script() if hasattr(capture, "_capture_script") else None
        instrumented_capture = instrument_capture(capture_script)
        instrumented_json_capture = instrument_capture(capture_script, json_transport=True)
        original_evaluate = native.Page.evaluate
        @wraps(original_evaluate)
        def page_evaluation(page, expression, *arguments, **options):
            phase = getattr(self._local, "phase", None)
            if expression not in (capture_script, json_capture_script) or phase is None:
                return self.measure("browser_reads", original_evaluate, page, expression, *arguments, **options)
            started = self._clock()
            response = self.measure("dom_extraction", original_evaluate, page,
                instrumented_capture if expression == capture_script else instrumented_json_capture,
                *arguments, **options)
            elapsed_millis = (self._clock() - started) * 1_000
            diagnostics = response["diagnostics"]
            diagnostics["phase"] = phase
            diagnostics["playwright_call_millis"] = elapsed_millis
            # Includes communication, decoding, scheduling and instrumentation overhead.
            diagnostics["outside_browser_capture_millis"] = (
                elapsed_millis - diagnostics["browser_millis"] - diagnostics["json_encoding_millis"]
                - diagnostics["size_measurement_millis"])
            self.dom_captures.append(diagnostics)
            return response["capture"]

        if json_capture_script is not None and json_capture_script != capture_script:
            self._patch(capture, "loads", "dom_json_decode")
        self._patch(evidence, "capture_page", "capture_and_widget_mapping")
        self._patch(evidence, "target_path", "target_resolution")
        if hasattr(evidence, "target_paths"):
            from testar_evidence_playwright import targets
            self._patch(evidence, "target_paths", "available_target_resolution")
            self._patch(targets, "_resolve_batch", "target_resolution_batch")
        self._patch(evidence.PlaywrightEvidence, "_password_target", "password_target_check", static=True)
        self._patch(native.Page, "screenshot", "screenshot")
        self._patches.enter_context(patch.object(native.Page, "evaluate", page_evaluation))
        reads = ("evaluate", "evaluate_all", "count", "get_attribute", "input_value", "text_content",
                 "is_enabled", "is_editable", "is_visible", "is_checked")
        for api_type in (native.Locator, native.ElementHandle, native.Frame):
            for name in reads:
                if hasattr(api_type, name):
                    self._patch(api_type, name, "browser_reads")
        for api_type, names in (
            (native.Page, facade_actions._PAGE_ACTIONS),
            (native.Locator, facade_actions._ELEMENT_ACTIONS),
            (native.ElementHandle, facade_actions._ELEMENT_ACTIONS),
            (native.Frame, facade_actions._FRAME_ACTIONS),
            (native.Keyboard, facade_actions._KEYBOARD_ACTIONS),
            (native.Mouse, facade_actions._MOUSE_ACTIONS),
            (native.Touchscreen, {"tap"}),
        ):
            for name in sorted(names):
                if hasattr(api_type, name):
                    self._patch(api_type, name, "native/" + api_type.__name__ + "." + name)
        # Patch imported aliases as well as their defining modules.
        for module in (records, storage):
            self._patch(module, "_prepare_event", "prepare_event")
            self._patch(module, "_validate_prepared_event", "schema_validation")
        for module in (records, codec):
            self._patch(module, "to_data", "convert_to_plain_data")
        self._patch(codec, "_dumps_prepared", "json_serialization")
        self._patch(ReconstructedEvidence, "_validate", "reference_and_lifecycle_validation")
        self._patch(ReconstructedEvidence, "_apply_prepared", "history_update")
        self._patch(storage.JsonlStore, "record", "record_event")
        self._patch(storage.JsonlStore, "put_artifact", "store_artifact")
        self._patch(storage, "_artifact", "verify_artifact")
        self._patch(storage, "_safe_path", "storage_path_checks")
        self._patch(Path, "read_bytes", lambda *args, **kwargs:
            "artifact_read" if self._inside("verify_artifact") else None)
        self._patch(storage.hashlib, "sha256", lambda *args, **kwargs:
            "artifact_hash" if self._inside("store_artifact") or self._inside("verify_artifact") else None)
        self._patch(storage.os, "fsync", lambda *args, **kwargs:
            "disk_sync" if self._inside("write_flush_sync") else None)
        original_write = storage._write_all
        @wraps(original_write)
        def write_all(output, data):
            if getattr(self._local, "phase", None) is None:
                return original_write(output, data)
            return self.measure("write_flush_sync", original_write, _MeasuredOutput(output, self), data)
        self._patches.enter_context(patch.object(storage, "_write_all", write_all))


class _MeasuredOutput:
    def __init__(self, output, timings):
        self._output = output
        self._timings = timings

    def __getattr__(self, name):
        return getattr(self._output, name)

    def write(self, data):
        written = self._timings.measure("file_write", self._output.write, data)
        phase = self._timings._local.phase
        self._timings._statistics[(phase, "file_write")]["bytes"] += max(0, written or 0)
        return written

    def flush(self):
        return self._timings.measure("file_flush", self._output.flush)
