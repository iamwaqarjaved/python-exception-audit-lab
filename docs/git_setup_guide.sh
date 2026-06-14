#!/usr/bin/env bash
# =============================================================================
# GIT SETUP GUIDE — python-exception-audit-lab
# Run these commands one block at a time in your terminal.
# Replace YOUR_USERNAME with your actual GitHub username.
# =============================================================================

# ── STEP 1: Create the repo on GitHub ────────────────────────────────────────
# Go to: https://github.com/new
# Name:         python-exception-audit-lab
# Description:  AI-assisted Python exception-handling audit lab with failure-injection tests and snapshot testing
# Visibility:   Public
# ✅ Do NOT check "Add a README" (we have one already)
# Click: Create repository

# ── STEP 2: On your Mac — clone or init ──────────────────────────────────────

# If you already have the files from this assignment locally:
cd ~/Desktop   # or wherever you want the project
git clone https://github.com/iamwaqarjaved/python-exception-audit-lab.git
cd python-exception-audit-lab

# OR if starting fresh — copy the downloaded files here, then:
# git init
# git remote add origin https://github.com/YOUR_USERNAME/python-exception-audit-lab.git

# ── STEP 3: Configure git identity (one-time on new Mac) ─────────────────────
git config --global user.name  "Waqar Javed"
git config --global user.email "waqar@agentsafelabs.io"

# ── STEP 4: Stage everything ──────────────────────────────────────────────────
git add .
git status   # review what's staged — should be all repo files

# ── STEP 5: Initial commit ───────────────────────────────────────────────────
git commit -m "feat: initial lab with 3 original files, refactored versions, and 30 failure-injection tests

- original/: file1 (bare except), file2 (no handling), file3 (mixed quality)
- refactored/: validated exception handling for all three files
- tests/: 30 pytest tests with mock injection and snapshot comparison
- conftest.py: sys.path setup + --snapshot-update fixture
- .github/workflows/ci.yml: CI on Python 3.10, 3.11, 3.12
- docs/findings.md: full validation table (5 unraisable, 3 missed)
- README.md: learning guide with quick-start, findings, and validation checklist"

# ── STEP 6: Push to GitHub ───────────────────────────────────────────────────
git branch -M main
git push -u origin main

# ── STEP 7: Add a version tag ────────────────────────────────────────────────
# Tags mark important milestones (visible on the repo's Releases page)

git tag -a v1.0.0 -m "v1.0.0 — Initial release

Complete Module 4 exception-handling audit lab:
- 5 unraisable exception findings proven against docs.python.org
- 3 missed realistic exception findings (Timeout, KeyError, ZeroDivisionError)
- 30 passing failure-injection tests on Python 3.10–3.12
- Snapshot testing infrastructure included"

git push origin v1.0.0

# ── STEP 8: Create a GitHub Release (via web) ────────────────────────────────
# Go to: https://github.com/YOUR_USERNAME/python-exception-audit-lab/releases/new
# Tag:     v1.0.0  (select the tag you just pushed)
# Title:   v1.0.0 — Module 4 Exception Audit Lab
# Description (paste this):
#
# ## What's included
# - 3 original buggy Python files (bare except, no handling, mixed quality)
# - 3 refactored files with validated exception handling
# - 30 failure-injection tests with mock patching
# - Snapshot testing — committed golden outputs in tests/snapshots/
# - CI via GitHub Actions (Python 3.10, 3.11, 3.12)
# - Full findings doc: 5 unraisable + 3 missed exceptions
#
# ## Quick start
# ```bash
# git clone https://github.com/YOUR_USERNAME/python-exception-audit-lab.git
# cd python-exception-audit-lab
# python3 -m venv .venv && source .venv/bin/activate
# pip install -r requirements.txt
# pytest tests/ -v --snapshot-update   # first run
# pytest tests/ -v                     # subsequent runs
# ```

# ── STEP 9: Future commits (example workflow) ─────────────────────────────────

# Adding a new finding:
git checkout -b finding/unraisable-typeerror-on-int-path
# ... make your changes ...
git add tests/test_failure_injection.py
git commit -m "test: prove TypeError unraisable on int path to open()

When path is always int (e.g. a file descriptor), TypeError cannot raise
because open() accepts int as a valid fd. Added test_open_with_fd_not_typeerror."
git push origin finding/unraisable-typeerror-on-int-path
# Then open a PR on GitHub

# Fixing a bug:
git checkout main
git checkout -b fix/summarize-empty-list-message
git commit -m "fix: improve ZeroDivisionError message in summarize()

Changed 'missing expected structure' to include the actual len(temps)
so callers can distinguish empty-list from missing-key errors."
git push origin fix/summarize-empty-list-message

# Bumping version after a batch of changes:
git tag -a v1.1.0 -m "v1.1.0 — Added coverage reporting and 3 new edge-case tests"
git push origin v1.1.0
