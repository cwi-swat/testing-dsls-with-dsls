# miniTESTAR tests

The tests in this folder were generated with Codex and refined together with
the project author. Their intended coverage is documented in TEST_PLAN.md.

These tests check miniTESTAR itself. They are separate from the website
scenarios in `src/testar/testingTESTAR.py` and `testingQLprograms.py`.

The test plan is documented in [TEST_PLAN.md](TEST_PLAN.md).

In VS Code, open the Testing panel (the flask icon in the left sidebar).
Use the Run Tests button to run all tests, or the play button beside an
individual test. Workspace settings configure unittest discovery in this folder.
If tests do not appear, refresh the panel and select a Python interpreter that
has Playwright installed using **Python: Select Interpreter**.

Alternatively, use **Terminal > Run Task > miniTESTAR: run all local tests**.
The existing F6 task for running the active Python file is unchanged.

Run all tests from the project directory:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Use a Python environment containing `playwright`. The Playwright tests also require its Chromium installation:

```bash
python3 -m playwright install chromium
```

The browser tests use local HTML in a headless browser, without contacting
external demo websites. The core tests verify sequence ordering and oracle
failure collection.

Keep tests aligned with intentional behavior changes. Do not remove a failing
check merely to make the suite pass: establish whether the implementation or
expectation is wrong. The current selector-based implementation does not verify
semantic target identity; these tests do not claim that it does.
