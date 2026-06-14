# file2_no_handling.py
# Student lab file – NO exception handling at all
# Uses: requests + Open-Meteo API, JSON parsing, file I/O

import json
import requests

CACHE_FILE = "weather_cache.json"
LAT = 25.9017
LON = -80.1577   # Pembroke Pines, FL


def fetch_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "current_weather": True,
    }
    response = requests.get(url, params=params)   # no timeout
    data = response.json()
    return data["current_weather"]["temperature"]  # assumes schema


def save_to_cache(temp):
    with open(CACHE_FILE, "w") as f:
        json.dump({"last_temp": temp}, f)


def load_from_cache():
    with open(CACHE_FILE, "r") as f:
        data = json.load(f)
    return data["last_temp"]


def display(temp):
    print(f"Current temperature: {temp}°C")


if __name__ == "__main__":
    temp = fetch_weather(LAT, LON)
    save_to_cache(temp)
    cached = load_from_cache()
    display(cached)
