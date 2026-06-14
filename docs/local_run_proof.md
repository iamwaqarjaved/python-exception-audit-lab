# Local Run Proof — macOS

Verified: **30/30 tests passing** on a real MacBook Pro.

| | |
|---|---|
| **Platform** | darwin (macOS) |
| **Python** | 3.10.5 |
| **pytest** | 9.1.0 |
| **pluggy** | 1.6.0 |
| **Run date** | June 14, 2026 |

---

## Step 1 — `pip install -r requirements.txt`

Installed: `requests 2.34.2`, `pytest 9.1.0`, `python-dotenv 1.2.2`, and all transitive deps.

![Install dependencies](screenshots/01_install_dependencies.png)

---

## Step 2 — `pytest tests/ -v --snapshot-update`

First run writes the 10 snapshot files to `tests/snapshots/`.  
**Result: 30 passed in 0.60s**

![Snapshot update — 30 passed](screenshots/02_snapshot_update_run.png)

---

## Step 3 — `pytest tests/ -v`

Clean run compares all outputs against committed snapshots.  
**Result: 30 passed in 0.13s**

![Clean run — 30 passed](screenshots/03_clean_test_run.png)

---

## What the screenshots prove

- The **snapshot workflow** works end-to-end: `--snapshot-update` writes, the clean run validates
- All **30 failure-injection tests** pass on Python 3.10 (not just 3.12 where they were built)
- The **`conftest.py` sys.path setup** works correctly — no manual `PYTHONPATH=` needed on macOS
- Dependencies install cleanly from `requirements.txt` with no conflicts
