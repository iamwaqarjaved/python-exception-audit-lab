# Exception Audit Findings

Full validation table from the AI audit of all three lab files.  
Validated against: `docs.python.org/3.12` and `requests.readthedocs.io`  
Test runner: Python 3.12.3, pytest 9.1.0 — **30 tests passing**

---

## Unraisable Exception Findings

### U-1 — TypeError on `open()` with hard-coded string path
- **File:** `file1_bare_except.py` → `load_config()`
- **AI suggestion:** catch `TypeError` on `open(CONFIG_PATH)`
- **Why unraisable:** `CONFIG_PATH = "config.json"` is a `str` literal. `open()` only raises `TypeError` when the first argument is not a `str`, `bytes`, or `os.PathLike`. A literal string is always valid.
- **Doc:** [docs.python.org/3/library/functions.html#open](https://docs.python.org/3/library/functions.html#open)

### U-2 — FileNotFoundError on `open(path, 'w')`
- **Files:** `file2_no_handling.py` → `save_to_cache()`, `file3_mixed.py` → `save_results()`
- **AI suggestion (and File 3 actually implemented this):** catch `FileNotFoundError`
- **Why unraisable:** `open()` in write mode calls `os.open()` with `O_CREAT | O_WRONLY | O_TRUNC`. The OS creates the file if absent. `FileNotFoundError` (errno `ENOENT`) only fires when a **parent directory** is missing. Paths with no directory components (`"weather_cache.json"`, `"results.json"`) have no missing parents.
- **Doc:** [docs.python.org/3/library/functions.html#open](https://docs.python.org/3/library/functions.html#open) — *"'w': open for writing... file is created if it does not exist."*

### U-3 — OverflowError on `float(string)`
- **File:** `file1_bare_except.py` → `parse_temperature()`
- **Why unraisable:** `float()` on a Python string raises `ValueError` (unparseable) or succeeds. `OverflowError` from `float()` only occurs in C-extension contexts when a C `double` overflows — not from Python string parsing.
- **Doc:** [docs.python.org/3/library/functions.html#float](https://docs.python.org/3/library/functions.html#float)

### U-4 — EnvironmentError from `os.environ` access
- **File:** `file1_bare_except.py` → `load_env_key()`
- **Why unraisable:** `EnvironmentError` has been a simple alias for `OSError` since Python 3.3 (PEP 3151). `os.environ.__getitem__` raises only `KeyError` for absent variables. It never raises `OSError`.
- **Doc:** [PEP 3151](https://peps.python.org/pep-3151/), [docs.python.org/3/library/os.html#os.environ](https://docs.python.org/3/library/os.html#os.environ)

### U-5 — UnicodeDecodeError from `response.json()`
- **File:** `file2_no_handling.py` → `fetch_weather()`
- **Why unraisable:** `requests.Response.json()` handles encoding detection internally via `self.text`. Any decoding problem is wrapped in `requests.exceptions.JSONDecodeError`. The caller never receives raw bytes.
- **Doc:** [requests.readthedocs.io — Response.json()](https://requests.readthedocs.io/en/latest/api/#requests.Response.json)

---

## Missed Realistic Exception Findings

### M-1 — `requests.exceptions.Timeout` (PRIMARY)
- **File:** `file2_no_handling.py` → `fetch_weather()`
- **Two-part problem:**
  1. No `timeout=` parameter → `Timeout` can **never fire**, not even with a handler
  2. Even after adding `timeout=10`, no handler was present
- **Fix:** `requests.get(url, params=params, timeout=10)` + `except requests.exceptions.Timeout`
- **Consequence without fix:** Infinite hang on slow server

### M-2 — `KeyError` on API schema mismatch
- **File:** `file2_no_handling.py` → `fetch_weather()`
- **Line:** `data["current_weather"]["temperature"]`
- **Why realistic:** API schemas change. Open-Meteo can return error responses without those keys.
- **Fix:** `except KeyError as exc: raise WeatherFetchError(...) from exc`

### M-3 — `ZeroDivisionError` in `summarize()`
- **File:** `file3_mixed.py` → `summarize()`
- **Line:** `sum(temps) / len(temps)`
- **Why realistic:** An empty forecast list is a valid API response for some date ranges.
- **Fix:** Caught via `except (KeyError, ZeroDivisionError)` → re-raised as `ValueError`

---

## Obsolete / Wrong Catches in File 3

| Catch | Problem | Fix |
|-------|---------|-----|
| `except ValueError` in `fetch_forecast()` | `requests` 2.28+ raises `JSONDecodeError`, not `ValueError` | Replace with `except requests.exceptions.JSONDecodeError` |
| `except IOError` in `fetch_forecast()` | `IOError` is `OSError` alias since Python 3.3; never raised by requests | Remove entirely |
| `except FileNotFoundError` in `save_results()` | Write mode creates the file; FNF cannot fire (see U-2) | Replace with `except OSError` |

---

## Full Validation Table

| File | Function | Exception | Verdict | Doc Source |
|------|----------|-----------|---------|-----------|
| File 1 | `load_config` | `FileNotFoundError` | ✅ Correct | docs.python.org/open |
| File 1 | `load_config` | `json.JSONDecodeError` | ✅ Correct | docs.python.org/json |
| File 1 | `load_config` | `TypeError` | ❌ Unraisable | Hard-coded str literal |
| File 1 | `get_api_key` | `KeyError` | ✅ Correct | docs.python.org/stdtypes |
| File 1 | `get_api_key` | `AttributeError` | ❌ Unraisable | dict[key] never raises AttributeError |
| File 1 | `write_log` | `OSError` | ✅ Correct | docs.python.org/open |
| File 1 | `parse_temperature` | `ValueError` | ✅ Correct | docs.python.org/float |
| File 1 | `parse_temperature` | `OverflowError` | ❌ Unraisable | C-extension only |
| File 1 | `load_env_key` | `KeyError` | ✅ Correct | docs.python.org/os.environ |
| File 1 | `load_env_key` | `EnvironmentError` | ❌ Unraisable | OSError alias; not raised by dict access |
| File 2 | `fetch_weather` | `requests.Timeout` | ✅ Correct + MISSED | requests.readthedocs.io |
| File 2 | `fetch_weather` | `UnicodeDecodeError` | ❌ Unraisable | requests decodes internally |
| File 2 | `fetch_weather` | `KeyError` (schema) | ✅ Correct | Python dict docs |
| File 2 | `save_to_cache` | `FileNotFoundError` on `'w'` | ❌ Unraisable | open() 'w' creates file |
| File 3 | `fetch_forecast` | `ValueError` from `.json()` | ❌ Wrong | requests 2.28+: JSONDecodeError |
| File 3 | `fetch_forecast` | `IOError` | ❌ Obsolete | Python 3.3+ alias; dead code |
| File 3 | `save_results` | `FileNotFoundError` on `'w'` | ❌ Unraisable | Same as File 2 |
| File 3 | `get_coordinates` | `ConnectionError` + `Timeout` | ✅ Correct (missed originally) | requests.readthedocs.io |
