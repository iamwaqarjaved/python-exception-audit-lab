# file2_refactored.py – full exception handling added to originally bare file
"""
AUDIT FINDINGS APPLIED:
  - Added timeout=10 to requests.get (prevents indefinite hang)
  - requests.exceptions.Timeout     → raised when timeout exceeded (MISSED by AI – see report)
  - requests.exceptions.ConnectionError → network unreachable
  - requests.exceptions.HTTPError   → non-2xx status via raise_for_status()
  - KeyError on data["current_weather"]["temperature"] → schema mismatch
  - FileNotFoundError on load_from_cache (cache may not exist yet)
  - json.JSONDecodeError on load_from_cache (corrupt cache file)

UNRAISABLE exception the AI suggested (proven in report):
  - UnicodeDecodeError on response.json(): requests always decodes internally;
    the caller never sees raw bytes to decode.
"""
import json
import requests
from typing import Optional

CACHE_FILE = "weather_cache.json"
LAT = 25.9017
LON = -80.1577


class WeatherFetchError(RuntimeError):
    """Raised when the weather API call fails for any reason."""


def fetch_weather(lat: float, lon: float) -> float:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "current_weather": True,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["current_weather"]["temperature"]
    except requests.exceptions.Timeout as exc:
        raise WeatherFetchError("Request timed out") from exc
    except requests.exceptions.ConnectionError as exc:
        raise WeatherFetchError("Network unreachable") from exc
    except requests.exceptions.HTTPError as exc:
        raise WeatherFetchError(f"HTTP error: {exc}") from exc
    except KeyError as exc:
        raise WeatherFetchError(f"Unexpected API schema – missing key {exc}") from exc


def save_to_cache(temp: float, path: str = CACHE_FILE) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"last_temp": temp}, f)
    except OSError as exc:
        print(f"Could not write cache: {exc}")


def load_from_cache(path: str = CACHE_FILE) -> Optional[float]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["last_temp"]
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    except KeyError:
        return None


def display(temp: Optional[float]) -> None:
    if temp is None:
        print("No temperature data available.")
    else:
        print(f"Current temperature: {temp}°C")


if __name__ == "__main__":
    try:
        temp = fetch_weather(LAT, LON)
        save_to_cache(temp)
    except WeatherFetchError as exc:
        print(f"Weather fetch failed: {exc}")
        temp = load_from_cache()
    display(temp)
