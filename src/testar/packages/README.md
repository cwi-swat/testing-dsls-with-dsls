# Install miniTESTAR's evidence packages

This folder contains the Python evidence library version `0.3.0` and Playwright adapter version `0.3.0`. These wheels install the library code; the adapter includes its automatic-recording facade and browser capture scripts.

Use Python 3.11 or later. From the repository root, run these commands with the Python environment you will use for miniTESTAR:

```sh
cd src/testar
python -m pip install -r requirements-evidence.txt
python -m playwright install chromium
```

On Linux, Playwright can also install Chromium's system dependencies:

```sh
python -m playwright install --with-deps chromium
```

The requirements file installs the two wheels included here. Pip downloads Playwright and its dependencies from the package index. Browser installation downloads Chromium. Each user installs packages and browsers on their own system; the evidence-library source repositories are not needed.

Run the scenarios selected in `testingTESTAR.py` from `src/testar`:

```sh
python testingTESTAR.py
```

The facade writes new traces under `target/traces`, relative to the directory where miniTESTAR is started. The repository's existing ignore rule excludes `target` directories from commits.

When distributing an updated library or adapter, rebuild its wheel from its source repository and update the corresponding filename in `requirements-evidence.txt`. Keep these wheels and the requirements file together in the branch.

This branch adds tool-level recording hooks. See [the integration notes](../EVIDENCE.md) and the `EVIDENCE` comments in the Python code.
