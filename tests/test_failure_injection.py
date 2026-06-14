"""
Module 4 – Failure-Injection Test Suite
========================================
Tests the REFACTORED versions of all three files.

Run locally:
    pip install -r requirements.txt
    pytest tests/ -v --snapshot-update   # first run: write snapshots
    pytest tests/ -v                     # subsequent runs: compare

Snapshot files land in tests/snapshots/ and are committed to the repo.
"""

import json
import pathlib
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest
import requests

import file1_refactored as f1
import file2_refactored as f2
import file3_refactored as f3

# ── Snapshot helper ────────────────────────────────────────────────────────
SNAPSHOT_DIR = pathlib.Path(__file__).parent / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)


def snap(name: str, value: str, update: bool) -> None:
    """Write or compare a plain-text snapshot."""
    path = SNAPSHOT_DIR / f"{name}.txt"
    if update or not path.exists():
        path.write_text(value)
        return
    expected = path.read_text()
    assert value == expected, (
        f"\nSnapshot mismatch for '{name}':\n"
        f"  Expected: {expected!r}\n"
        f"  Got:      {value!r}\n"
        f"\nRe-run with --snapshot-update to accept the new value."
    )


@pytest.fixture
def snapshot(request):
    """Pytest fixture: passes a snap() callable pre-bound to --snapshot-update flag."""
    update = request.config.getoption("--snapshot-update", default=False)
    return lambda name, value: snap(name, value, update)


def pytest_addoption(parser):
    parser.addoption(
        "--snapshot-update",
        action="store_true",
        default=False,
        help="Overwrite existing snapshots with current output.",
    )


# ══════════════════════════════════════════════════════════════════════════
# FILE 1 TESTS
# ══════════════════════════════════════════════════════════════════════════
class TestFile1:

    def test_load_config_missing_file(self):
        """FileNotFoundError → returns empty dict."""
        result = f1.load_config("/no/such/file.json")
        assert result == {}

    def test_load_config_bad_json(self):
        """JSONDecodeError → returns empty dict."""
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write("{bad json")
            tmp = f.name
        result = f1.load_config(tmp)
        assert result == {}

    def test_load_config_valid(self, snapshot):
        """Valid JSON config → returns dict, snapshot the keys."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as f:
            json.dump({"api_key": "test-key-123", "timeout": 10}, f)
            tmp = f.name
        result = f1.load_config(tmp)
        snapshot("load_config_valid_keys", str(sorted(result.keys())))

    def test_get_api_key_missing_key(self):
        """KeyError on absent key → returns None explicitly."""
        assert f1.get_api_key({}) is None

    def test_get_api_key_present(self, snapshot):
        """Key present → returns value; snapshot the type."""
        result = f1.get_api_key({"api_key": "abc123"})
        assert result == "abc123"
        snapshot("get_api_key_type", type(result).__name__)

    def test_parse_temperature_valid(self, snapshot):
        """Valid numeric string → float, snapshot formatted output."""
        result = f1.parse_temperature("22.7")
        assert result == pytest.approx(22.7)
        snapshot("parse_temp_valid", f"{result:.2f}")

    def test_parse_temperature_invalid(self):
        """Non-numeric string → returns None (not silent 0.0)."""
        assert f1.parse_temperature("22.7abc") is None

    def test_parse_temperature_none_not_zero(self):
        """Confirms the fix: bad input must NOT silently return 0.0."""
        result = f1.parse_temperature("not-a-number")
        assert result != 0.0, "Silent 0.0 on bad input is a data corruption bug"
        assert result is None

    def test_keyboard_interrupt_not_swallowed(self):
        """Refactored code must NOT catch KeyboardInterrupt (bare except trap)."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as f:
            json.dump({"api_key": "x"}, f)
            tmp = f.name
        with patch("json.load", side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                f1.load_config(tmp)

    def test_load_env_key_absent(self, monkeypatch):
        """Absent env var → returns empty string (KeyError caught)."""
        monkeypatch.delenv("WEATHER_API_KEY", raising=False)
        assert f1.load_env_key() == ""

    def test_load_env_key_present(self, monkeypatch, snapshot):
        """Env var present → returns its value; snapshot the value."""
        monkeypatch.setenv("WEATHER_API_KEY", "my-secret-key")
        result = f1.load_env_key()
        assert result == "my-secret-key"
        snapshot("load_env_key_present", result)


# ══════════════════════════════════════════════════════════════════════════
# FILE 2 TESTS
# ══════════════════════════════════════════════════════════════════════════
class TestFile2:

    @patch("requests.get")
    def test_fetch_weather_success(self, mock_get, snapshot):
        """Happy path → returns temperature float; snapshot the value."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"current_weather": {"temperature": 31.5}}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        temp = f2.fetch_weather(25.9, -80.1)
        assert temp == 31.5
        snapshot("fetch_weather_success", str(temp))

    @patch("requests.get", side_effect=requests.exceptions.Timeout)
    def test_fetch_weather_timeout(self, _):
        """Timeout → raises WeatherFetchError (not unhandled Timeout)."""
        with pytest.raises(f2.WeatherFetchError, match="timed out"):
            f2.fetch_weather(25.9, -80.1)

    @patch("requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_fetch_weather_connection_error(self, _):
        """ConnectionError → raises WeatherFetchError."""
        with pytest.raises(f2.WeatherFetchError, match="Network"):
            f2.fetch_weather(25.9, -80.1)

    @patch("requests.get")
    def test_fetch_weather_missing_key(self, mock_get, snapshot):
        """Schema mismatch KeyError → WeatherFetchError; snapshot message prefix."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"unexpected": {}}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        with pytest.raises(f2.WeatherFetchError) as exc_info:
            f2.fetch_weather(25.9, -80.1)
        msg = str(exc_info.value)
        snapshot("fetch_weather_schema_error_msg", msg)

    @patch("requests.get")
    def test_fetch_weather_http_error(self, mock_get):
        """HTTP 500 → WeatherFetchError."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
        mock_get.return_value = mock_resp
        with pytest.raises(f2.WeatherFetchError, match="HTTP"):
            f2.fetch_weather(25.9, -80.1)

    def test_load_from_cache_missing(self):
        """Cache file absent → returns None (not FileNotFoundError crash)."""
        result = f2.load_from_cache("/no/such/cache.json")
        assert result is None

    def test_load_from_cache_bad_json(self):
        """Corrupted cache → returns None (not JSONDecodeError crash)."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as f:
            f.write("not valid json{{")
            tmp = f.name
        result = f2.load_from_cache(tmp)
        assert result is None

    def test_save_and_load_roundtrip(self, snapshot):
        """save_to_cache + load_from_cache roundtrip; snapshot the value."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp = f.name
        f2.save_to_cache(28.3, path=tmp)
        result = f2.load_from_cache(path=tmp)
        assert result == pytest.approx(28.3)
        snapshot("cache_roundtrip_value", str(result))


# ══════════════════════════════════════════════════════════════════════════
# FILE 3 TESTS
# ══════════════════════════════════════════════════════════════════════════
class TestFile3:

    @patch("requests.get")
    def test_get_coordinates_success(self, mock_get, snapshot):
        """Valid geocoding response → returns (lat, lon); snapshot tuple."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "results": [{"latitude": 25.77, "longitude": -80.19}]
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        lat, lon = f3.get_coordinates("Miami")
        assert lat == pytest.approx(25.77)
        snapshot("get_coordinates_miami", f"lat={lat}, lon={lon}")

    @patch("requests.get", side_effect=requests.exceptions.Timeout)
    def test_get_coordinates_timeout(self, _):
        """Timeout → RuntimeError with 'timed out' message."""
        with pytest.raises(RuntimeError, match="timed out"):
            f3.get_coordinates("Miami")

    @patch("requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_get_coordinates_connection_error(self, _):
        """ConnectionError → RuntimeError."""
        with pytest.raises(RuntimeError, match="Network error"):
            f3.get_coordinates("Miami")

    @patch("requests.get")
    def test_get_coordinates_no_results(self, mock_get):
        """City not found (empty/absent results) → RuntimeError."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        with pytest.raises(RuntimeError, match="No geocoding result"):
            f3.get_coordinates("XYZNonExistentCity999")

    @patch("requests.get")
    def test_fetch_forecast_json_decode_error(self, mock_get):
        """requests.JSONDecodeError (NOT ValueError) → returns {} gracefully."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.side_effect = requests.exceptions.JSONDecodeError(
            "bad", "", 0
        )
        mock_get.return_value = mock_resp
        result = f3.fetch_forecast(25.77, -80.19)
        assert result == {}

    @patch("requests.get", side_effect=requests.exceptions.Timeout)
    def test_fetch_forecast_timeout(self, _):
        """Timeout → returns {} (degraded mode, not crash)."""
        result = f3.fetch_forecast(25.77, -80.19)
        assert result == {}

    def test_summarize_valid(self, snapshot):
        """Valid forecast dict → formatted string; snapshot it."""
        forecast = {"daily": {"temperature_2m_max": [30.0, 31.0, 29.0]}}
        result = f3.summarize(forecast)
        assert "30.0" in result
        snapshot("summarize_valid_output", result)

    def test_summarize_missing_key(self):
        """Missing 'daily' key → ValueError with clear message (not bare KeyError)."""
        with pytest.raises(ValueError, match="missing expected structure"):
            f3.summarize({})

    def test_summarize_empty_temps(self):
        """Empty temperature list → ValueError (ZeroDivisionError caught+wrapped)."""
        with pytest.raises(ValueError, match="missing expected structure"):
            f3.summarize({"daily": {"temperature_2m_max": []}})

    def test_save_and_load_results_roundtrip(self, snapshot):
        """save_results + load_results roundtrip; snapshot the key."""
        data = {"daily": {"temperature_2m_max": [29.5, 30.1]}}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp = f.name
        f3.save_results(data, path=tmp)
        loaded = f3.load_results(path=tmp)
        assert loaded == data
        snapshot("results_roundtrip_key", str(list(loaded.keys())))

    def test_load_results_missing_file(self):
        """Missing results file → returns {} (not crash)."""
        result = f3.load_results("/no/such/results.json")
        assert result == {}
