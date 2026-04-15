import pytest
from unittest.mock import patch, MagicMock
from smart_anagram import get_available_ram, group_anagrams_smart

_LARGE_RAM  = 8 * 1024 * 1024 * 1024   # 8 GB  → file will be below threshold
_SMALL_RAM  = 1                          # 1 B   → 15% threshold is sub-byte; any file exceeds it


# ---------------------------------------------------------------------------
# get_available_ram — cross-platform graceful degradation
# ---------------------------------------------------------------------------

def test_get_available_ram_returns_int_on_macos():
    """On macOS the function should return a positive integer without raising."""
    with patch("smart_anagram.platform.system", return_value="Darwin"):
        result = get_available_ram()
    assert isinstance(result, int)
    assert result > 0


def test_fallback_on_linux(capsys):
    """On Linux the function must not crash and must return the fixed fallback."""
    with patch("smart_anagram.platform.system", return_value="Linux"):
        result = get_available_ram()
    assert result == 100 * 1024 * 1024
    assert "WARNING" in capsys.readouterr().err


def test_fallback_on_windows(capsys):
    with patch("smart_anagram.platform.system", return_value="Windows"):
        result = get_available_ram()
    assert result == 100 * 1024 * 1024


def test_fallback_when_sysctl_fails(capsys):
    """If sysctl raises on macOS the fallback must still be returned cleanly."""
    import subprocess
    with patch("smart_anagram.platform.system", return_value="Darwin"):
        with patch("smart_anagram.subprocess.check_output",
                   side_effect=subprocess.CalledProcessError(1, "sysctl")):
            result = get_available_ram()
    assert result == 100 * 1024 * 1024
    assert "WARNING" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Dispatcher routing
# ---------------------------------------------------------------------------

def test_selects_naive_for_small_file(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "tea", "tan"])
    with patch("smart_anagram.get_available_ram", return_value=_LARGE_RAM):
        with patch("smart_anagram.run_with_stats") as mock_run:
            group_anagrams_smart(path)
            label = mock_run.call_args[0][0]
    assert "Naive" in label


def test_selects_external_for_large_file(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "tea", "tan"])
    with patch("smart_anagram.get_available_ram", return_value=_SMALL_RAM):
        with patch("smart_anagram.run_with_stats") as mock_run:
            group_anagrams_smart(path)
            label = mock_run.call_args[0][0]
    assert "External" in label


def test_memory_error_triggers_fallback(tmp_word_file, capsys):
    """When the scaled approach raises MemoryError, external must be used."""
    path = tmp_word_file(["eat", "tea"])
    calls = []

    def fake_run(label, fn, fp):
        calls.append(label)
        if "Naive" in label:
            raise MemoryError

    with patch("smart_anagram.get_available_ram", return_value=_LARGE_RAM):
        with patch("smart_anagram.run_with_stats", side_effect=fake_run):
            group_anagrams_smart(path)

    assert any("Naive" in c for c in calls)
    assert any("External" in c for c in calls)
