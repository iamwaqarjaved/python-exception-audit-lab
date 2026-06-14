# file3_mixed.py
# Student lab file – mixed quality exception handling
# Uses: requests + Open-Meteo, JSON, dotenv, file I/O

import json
import os
import requests

RESULTS_FILE = "results.json"


def get_coordinates(city: str) -> tuple:
    """Geocode city name via Open-Meteo geocoding endpoint."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        resp = requests.get(url, params={"name": city, "count": 1})
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:          # catches HTTP errors
        raise RuntimeError(f"Geocoding failed: {e}")
    # ---- no handling for network-level failures ----
    data = resp.json()
    result = data["results"][0]                         # KeyError if no match
    return result["latitude"], result["longitude"]


def fetch_forecast(lat: float, lon: float) -> dict:
    """Fetch 7-day daily max temp from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "daily":     "temperature_2m_max",
        "timezone":  "auto",
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except ValueError:                                  # swallowed – wrong exc
        return {}
    except IOError:                                     # obsolete alias
        return {}


def save_results(data: dict, path: str = RESULTS_FILE):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except FileNotFoundError:                           # cannot raise on write
        print("Could not save results")
    except PermissionError:
        print("Permission denied writing results")


def load_results(path: str = RESULTS_FILE) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def summarize(forecast: dict) -> str:
    temps = forecast["daily"]["temperature_2m_max"]     # KeyError possible
    avg   = sum(temps) / len(temps)
    return f"7-day avg max: {avg:.1f}°C"


if __name__ == "__main__":
    lat, lon = get_coordinates("Miami")
    forecast = fetch_forecast(lat, lon)
    save_results(forecast)
    loaded = load_results()
    print(summarize(loaded))
