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
