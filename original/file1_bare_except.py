# file1_bare_except.py
# Student lab file – bare except clauses everywhere (over-catching)
# Uses: file I/O, JSON parsing, environment variable loading

import json
import os

CONFIG_PATH = "config.json"
LOG_PATH    = "app.log"


def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        return data
    except:                          # <-- bare except #1
        print("Could not load config")
        return {}


def get_api_key(config):
    try:
        return config["api_key"]
    except:                          # <-- bare except #2
        return None


def write_log(message):
    try:
        with open(LOG_PATH, "a") as f:
            f.write(message + "\n")
    except:                          # <-- bare except #3
        pass


def parse_temperature(raw):
    try:
        value = float(raw)
        return round(value, 2)
    except:                          # <-- bare except #4
        return 0.0


def load_env_key():
    try:
        key = os.environ["WEATHER_API_KEY"]
        return key
    except:                          # <-- bare except #5
        return ""


if __name__ == "__main__":
    cfg = load_config()
    key = get_api_key(cfg) or load_env_key()
    write_log(f"Started with key={key!r}")
    print(parse_temperature("22.7abc"))
