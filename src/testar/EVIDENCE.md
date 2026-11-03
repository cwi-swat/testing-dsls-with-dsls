# Intermediate evidence integration

The Playwright facade captures observations, individual browser operations, and their outcomes. This intermediate integration adds miniTESTAR's available actions and custom oracle results.

`miniTESTAR.configure_steps(...)` wraps the original `TESTARSteps` in `RecordingTESTARSteps`, followed by `PerformanceTESTARSteps` when timing is enabled. Demo entry points use the ordinary `testar(...)` function with named arguments. The test loop delegates to the configured steps. Search for `# EVIDENCE` in `recording_steps.py` to find the recording points.

## 1. Available actions: what could be selected

The wrapper's `record_available_actions(...)` converts miniTESTAR's action descriptions into the adapter's `AvailableAction` values. Their scope is `eligible`: these choices passed the tool's selectors and filters, with reachability checked later.

The wrapper saves the choices at their discovery observation, including unselected actions, planning parameters, and widget bindings when available. After a target is skipped, it records the reduced list. The list is saved separately from the facade's browser-operation descriptions.

## 2. Browser operations: what was executed

The facade automatically records ordinary Playwright operations and their outcomes. Preparation calls, such as entering a username, entering a password, and clicking Sign in, remain separate actions.

For miniTESTAR text-entry actions, the backend offers an optional `compound_action_runner` hook after reachability checks and input generation. `RecordingTESTARSteps` uses `perform(..., record_operations=True)` to record clearing or positioning the cursor, typing, and pressing Enter as one compound execution linked to the selected available action. The original native calls, input modes, and exception handling remain in the backend.

The source and result are captured once. An `application/json` artifact on the result observation retains the ordered native methods, supplied parameters, and outcomes, including operations completed before a failure. The adapter redacts password arguments. Intermediate GUI captures are omitted. The runner is restored after execution; skipped targets do not create compound executions.

## 3. Custom oracle results

The wrapper decorates individual oracle callbacks and delegates to the original `TESTARSteps.check_oracles(...)`. Each callback runs once; its original finding handling and interactive error pause remain in place. `record_oracle_result(...)` saves its passed, failed, or error result and any reported error.

A generic callback result targets the observation and has an unknown observed value. It does not identify which individual widgets or properties were checked. Oracles using the facade's `expect` can additionally record detailed native checks. Explicit targets and values can be supplied through `evidence_for(page).checks.evaluate(...)`.

The facade records preparation operations and manages trace start, end, and required identifiers. See the [package installation instructions](packages/README.md). Traces are written under the default `target/traces` directory.
