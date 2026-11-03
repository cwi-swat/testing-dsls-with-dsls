# Recording benchmark

This benchmark compares `TESTARSteps` using native Playwright with
`RecordingTESTARSteps` using the evidence adapter. Both use the real miniTESTAR
`PlaywrightSession`, the same browser settings, and the same local HTML page.
The existing scenario configuration is unchanged.

From the repository root, using an environment with the bundled evidence packages
and Playwright's Chromium installed:

```powershell
python -X utf8 benchmarks/benchmark_recording.py
```

The default performs one warm-up pair and three measured pairs, with 20 actions
per execution. Each pair alternates which mode runs first. The fixed action
sequence types supplied text and presses Enter, selects an option, submits the
form, presses an arrow key, and clears the form. It repeats as needed. Both modes
derive the full available-action list and execute the same selected descriptions.
One custom oracle checks the form values and submission count after every action.

Recording groups text entry into one compound execution while retaining its three
native operations in a referenced JSON artifact. The benchmark validates these
operation details as well as the recorded transitions. Native mode executes the
same browser operations.

The summary reports median timings per stage and for the complete execution.
Results, per-execution logs, and recording traces are saved in a new directory
under `target/benchmarks`. `results.json` includes every sample, browser/package
versions, workload hashes, and evidence counts. Warm-ups are excluded from medians.
Complete totals include benchmark loop administration; individual stage medians
need not add up to the total median.

The benchmark rejects failed actions, oracle findings, unequal workloads, and
invalid recorded evidence. Evidence validation, including screenshot hashes,
runs after the execution timer stops. There is no fixed speed threshold: compare
timings on the same machine and settings.

Use `--actions 5 --repeats 1 --warmups 0` for a short check. Use `--channel chrome`
to select an installed Chrome instead of bundled Chromium. `--widgets` controls
additional DOM elements and `--extra-buttons` controls additional available
click actions. Screenshots use the adapter's normal settings; `--no-screenshots`
allows a separate comparison of recording without screenshots.

## Compare recording with and without screenshots

From the repository root, run 50 actions per execution, with one warm-up pair
and two measured pairs for each command.

With screenshots:

```powershell
python -X utf8 benchmarks/benchmark_recording.py --actions 50 --repeats 2 --warmups 1
```

Without screenshots:

```powershell
python -X utf8 benchmarks/benchmark_recording.py --actions 50 --repeats 2 --warmups 1 --no-screenshots
```

## Locate recording costs

Add `--breakdown` to measure internals in the benchmark process. The temporary
wrappers delegate the original operations, retain disk synchronization, and are
removed after each execution. The production libraries and adapter are unchanged.

Start with the same workload in both commands:

```powershell
python -X utf8 benchmarks/benchmark_recording.py --actions 50 --repeats 2 --warmups 1 --breakdown
python -X utf8 benchmarks/benchmark_recording.py --actions 50 --repeats 2 --warmups 1 --breakdown --no-screenshots
```

The console shows median breakdowns for execution and discovery. `Rec` means
recording mode. Each sample in `results.json` contains a `breakdown` list for all
stages and both modes, including call counts, failures, total/self time, average
and maximum call duration, and written bytes. Warm-ups retain their diagnostic
rows but are excluded from the console medians.

`total_seconds` includes measured child calls. `self_seconds` excludes them;
do not add inclusive totals together. `phase_total` is the complete timed step,
with its self time representing work outside the other measured calls. Medians
of individual rows need not add up exactly.

The main rows identify:

- `dom_extraction`: the capture script's browser call, including transferring
  the returned data to Python.
- `capture_and_widget_mapping`: complete capture; its self time includes Python
  widget creation and capture administration outside DOM extraction/screenshots.
- `screenshot`: obtaining PNG bytes from Playwright.
- `native/...` and `browser_reads`: original Playwright calls, including browser
  waiting and communication. Target/password helpers include their nested reads.
- `available_target_resolution`: resolving a complete reported available-action
  list. `target_resolution_batch` counts browser batches for supported CSS targets;
  `target_resolution` counts individual resolutions, including native fallbacks.
  These rows include nested `browser_reads`; do not add their inclusive totals.
- Event preparation, conversion, schema/reference validation, serialization,
  history updates, artifact storage/verification, path checks, writes, flushes,
  and `disk_sync`: the corresponding recording work.

Trace reconstruction and artifact verification after the execution remain
outside the diagnostics. Instrumentation adds overhead: use it to locate costs,
then compare improvements with ordinary runs without `--breakdown`.

To investigate scaling, change one input at a time. Keep `--extra-buttons 10`
while comparing `--widgets 100` and `--widgets 300`. Then keep `--widgets 100`
while comparing `--extra-buttons 10` and `--extra-buttons 30`.

The timing-accounting checks can be run without launching a browser:

```powershell
python -m unittest discover -s benchmarks -p test_timing_breakdown.py
```

### Inspect DOM capture costs

With `--breakdown`, a temporary instrumented copy of the installed capture script
measures property reads in the browser: attributes, text, live values, bounds and
computed styles. Traversal and result construction are reported as the remaining
browser time. Property stages include the work to save their values and aliases.
These timings overlap `dom_extraction`; do not add them to that row.

The console shows execution medians. Each sample's `dom_captures` list in
`results.json` also records every capture's stage, widget/property counts and
UTF-8 JSON size. This is the size of the capture data encoded as JSON, not the
Playwright protocol's actual wire size. Diagnostic metadata is removed before
returning the data to the adapter; evidence contents stay unchanged.

`outside_browser_capture_millis` subtracts JavaScript capture, browser JSON
encoding, and the separately measured JSON-size calculation from the complete
Playwright call. It estimates
communication/decoding costs together with scheduling and diagnostic overhead;
it does not isolate network transfer. Browser timings include instrumentation
and can be coarse for short operations. The extra JSON encoding used to measure
size also makes diagnostic runs slower. JSON transport reuses the encoded text
for this measurement; object transport encodes a copy only for diagnostics.
`json_encoding_millis` measures browser encoding for JSON transport, while
`dom_json_decode` measures Python decoding in the main breakdown.

Compare 50, 100 and 300 widgets while keeping actions and extra buttons fixed:

```powershell
python -X utf8 benchmarks/benchmark_recording.py --actions 50 --repeats 2 --warmups 1 --widgets 100 --extra-buttons 10 --no-screenshots --breakdown
```

Change only `--widgets` between runs. The optional browser test compares the
original and instrumented capture outputs, including redaction, shadow roots,
and capture limits. Enable it with `$env:TESTAR_BROWSER_TESTS="1"` before running
the timing-accounting checks above; it uses installed Chrome by default.

### Compare capture transport

The adapter transports captures as JSON text. `--capture-transport object` is a
benchmark-only comparison with the previous nested-object transport. It keeps
batch target resolution and all capture settings the same. Both modes still
validate their traces after timing. This option also works without `--breakdown`.

```powershell
python -X utf8 benchmarks/benchmark_recording.py --actions 50 --repeats 2 --warmups 1 --widgets 100 --extra-buttons 10 --no-screenshots --capture-transport object
python -X utf8 benchmarks/benchmark_recording.py --actions 50 --repeats 2 --warmups 1 --widgets 100 --extra-buttons 10 --no-screenshots --capture-transport json
```

Add `--breakdown` to inspect browser extraction, JSON encoding, the complete
Playwright call, and Python decoding. Use identical inputs for both comparisons;
change only the transport. The selected transport is saved in `results.json`.
