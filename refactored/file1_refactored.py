# file1_refactored.py – validated exception handling replacing bare excepts
"""
AUDIT FINDINGS APPLIED:
  bare except #1 (load_config)  → FileNotFoundError | json.JSONDecodeError
  bare except #2 (get_api_key)  → KeyError
  bare except #3 (write_log)    → OSError  (covers PermissionError, IsADirectoryError, etc.)
  bare except #4 (parse_temp)   → ValueError
  bare except #5 (load_env_key) → KeyError  (os.environ raises KeyError, NOT KeyboardInterrupt)

UNRAISABLE exceptions NOT caught (validated against docs.python.org):
  - TypeError: open() with a str path cannot raise TypeError on a hard-coded str constant
  - AttributeError: json.load() on a valid file object cannot raise AttributeError
"""
import json
import os
from typing import Any, Optional

CONFIG_PATH = "config.json"
LOG_PATH    = "app.log"


def load_config(path: str = CONFIG_PATH) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {path!r}")
        return {}
    except json.JSONDecodeError as exc:
        print(f"Config file is not valid JSON: {exc}")
        return {}
    # OSError (PermissionError etc.) intentionally propagates – caller must handle


def get_api_key(config: dict) -> Optional[str]:
    try:
        return config["api_key"]
    except KeyError:
        return None


def write_log(message: str, path: str = LOG_PATH) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except OSError as exc:
        # OSError covers PermissionError, IsADirectoryError, etc.
        print(f"Logging failed: {exc}")


def parse_temperature(raw: Any) -> Optional[float]:
    try:
        return round(float(raw), 2)
    except ValueError:
        # float() raises ValueError on unconvertible strings – documented.
        return None


def load_env_key() -> str:
    try:
        return os.environ["WEATHER_API_KEY"]
    except KeyError:
        # os.environ.__getitem__ raises KeyError when key absent – documented.
        return ""


if __name__ == "__main__":
    cfg = load_config()
    key = get_api_key(cfg) or load_env_key()
    write_log(f"Started with key={key!r}")
    print(parse_temperature("22.7abc"))
