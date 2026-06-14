"""
Root conftest.py
- Adds refactored/ to sys.path so tests can import file1_refactored etc.
- Registers --snapshot-update CLI option
- Provides the `snapshot` fixture used by all test files
"""
import sys
import pathlib
import pytest

# Make refactored/ importable without installing as a package
sys.path.insert(0, str(pathlib.Path(__file__).parent / "refactored"))

SNAPSHOT_DIR = pathlib.Path(__file__).parent / "tests" / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)


def pytest_addoption(parser):
    parser.addoption(
        "--snapshot-update",
        action="store_true",
        default=False,
        help="Overwrite existing snapshots with current output.",
    )


def _snap(name: str, value: str, update: bool) -> None:
    """Write or compare a plain-text snapshot file."""
    path = SNAPSHOT_DIR / f"{name}.txt"
    if update or not path.exists():
        path.write_text(value)
        return
    expected = path.read_text()
    assert value == expected, (
        f"\nSnapshot mismatch for '{name}':\n"
        f"  Expected: {expected!r}\n"
        f"  Got:      {value!r}\n"
        f"\nRe-run with --snapshot-update to accept new output."
    )


@pytest.fixture
def snapshot(request):
    """Usage: def test_foo(snapshot): snapshot('my_name', result)"""
    update = request.config.getoption("--snapshot-update", default=False)
    return lambda name, value: _snap(name, value, update)
