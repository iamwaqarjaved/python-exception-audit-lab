# file3_refactored.py – corrected mixed-quality exception handling
"""
AUDIT FINDINGS APPLIED:

  REMOVED unraisable exceptions:
    - FileNotFoundError in save_results(): open() in write mode creates the
      file if absent; FileNotFoundError only raises if intermediate directories
      are missing. Replaced with OSError which covers PermissionError and
      IsADirectoryError (both realistic).
    - ValueError in fetch_forecast(): requests never raises ValueError for bad
      response bodies; it raises requests.exceptions.JSONDecodeError
      (a subclass of json.JSONDecodeError, NOT ValueError since requests 2.28).
    - IOError in fetch_forecast(): IOError is an obsolete alias for OSError in
      Python 3 and is never raised by requests. Removed entirely.

  ADDED missing realistic exceptions:
    - requests.exceptions.ConnectionError in get_coordinates()
    - requests.exceptions.Timeout in get_coordinates()
    - KeyError in get_coordinates() when 'results' key absent or list empty
    - KeyError in summarize() re-raised as ValueError with a clear message
    - requests.exceptions.JSONDecodeError in fetch_forecast()
"""
import json
import requests
from typing import Optional

RESULTS_FILE = "results.json"


def get_coordinates(city: str) -> tuple:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        resp = requests.get(url, params={"name": city, "count": 1}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        result = data["results"][0]          # IndexError if list empty
        return result["latitude"], result["longitude"]
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(f"Geocoding timed out for {city!r}") from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(f"Network error during geocoding: {exc}") from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Geocoding HTTP error: {exc}") from exc
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"No geocoding result for {city!r}: {exc}") from exc


def fetch_forecast(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "daily":     "temperature_2m_max",
        "timezone":  "auto",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {}
    except requests.exceptions.ConnectionError:
        return {}
    except requests.exceptions.HTTPError:
        return {}
    except requests.exceptions.JSONDecodeError:
        # requests 2.28+ raises this, NOT ValueError
        return {}


def save_results(data: dict, path: str = RESULTS_FILE) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        # Covers PermissionError, IsADirectoryError, disk-full (ENOSPC), etc.
        # FileNotFoundError is NOT caught here: open() in "w" mode never raises
        # it for the target file itself; only missing parent dirs cause it.
        print(f"Could not save results: {exc}")


def load_results(path: str = RESULTS_FILE) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def summarize(forecast: dict) -> str:
    try:
        temps = forecast["daily"]["temperature_2m_max"]
        avg   = sum(temps) / len(temps)
        return f"7-day avg max: {avg:.1f}°C"
    except (KeyError, ZeroDivisionError) as exc:
        raise ValueError(f"Forecast data missing expected structure: {exc}") from exc


if __name__ == "__main__":
    lat, lon = get_coordinates("Miami")
    forecast = fetch_forecast(lat, lon)
    save_results(forecast)
    loaded = load_results()
    print(summarize(loaded))
