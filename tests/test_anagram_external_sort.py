import pytest
import tempfile
import os
import random
import string
from unittest.mock import patch, MagicMock

from group_anagrams import group_anagrams as naive
from anagram_external_sort import group_anagrams as external


def _parse_stdout(captured: str) -> set[frozenset[str]]:
    groups = set()
    for line in captured.strip().splitlines():
        words = line.strip().split()
        if words:
            groups.add(frozenset(words))
    return groups


# ---------------------------------------------------------------------------
# Correctness
# ---------------------------------------------------------------------------

def test_basic_grouping(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "tea", "tan", "nat", "bat"])
    external(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {
        frozenset(["eat", "tea"]),
        frozenset(["tan", "nat"]),
        frozenset(["bat"]),
    }


def test_single_word(tmp_word_file, capsys):
    path = tmp_word_file(["hello"])
    external(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset(["hello"])}


def test_all_unique(tmp_word_file, capsys):
    words = ["cat", "dog", "bird"]
    path = tmp_word_file(words)
    external(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset([w]) for w in words}


def test_all_same_anagram(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "tea", "ate"])
    external(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset(["eat", "tea", "ate"])}


def test_case_insensitive_grouping(tmp_word_file, capsys):
    path = tmp_word_file(["Eat", "tEa"])
    external(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset(["Eat", "tEa"])}


def test_preserves_original_case(tmp_word_file, capsys):
    path = tmp_word_file(["Eat", "Tea"])
    external(path)
    out = capsys.readouterr().out
    assert "Eat" in out
    assert "Tea" in out


def test_ignores_blank_lines(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "", "tea", "", "bat"])
    external(path)
    result = _parse_stdout(capsys.readouterr().out)
    flat = [w for g in result for w in g]
    assert "" not in flat
    assert len(flat) == 3


def test_utf8_words(tmp_word_file, capsys):
    path = tmp_word_file(["café", "naïve", "résumé"])
    # Must not raise UnicodeDecodeError or UnicodeEncodeError
    external(path)
    out = capsys.readouterr().out
    assert out.strip() != ""


# ---------------------------------------------------------------------------
# Subprocess failure paths
# ---------------------------------------------------------------------------

def test_sort_not_available(tmp_word_file):
    path = tmp_word_file(["eat", "tea"])
    with patch("anagram_external_sort.subprocess.Popen", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            external(path)


def test_sort_nonzero_exit(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "tea"])

    mock_proc = MagicMock()
    mock_proc.stdin = MagicMock()
    mock_proc.stdout = iter([])
    mock_proc.stderr.read.return_value = "sort: disk full"
    mock_proc.returncode = 1
    mock_proc.wait.return_value = None

    with patch("anagram_external_sort.subprocess.Popen", return_value=mock_proc):
        with pytest.raises(RuntimeError, match="sort failed"):
            external(path)


# ---------------------------------------------------------------------------
# Scale — output matches naive on large input
# ---------------------------------------------------------------------------

def test_large_file_output_matches_naive(capsys):
    words = []
    rng = random.Random(42)
    for _ in range(50_000):
        word = "".join(rng.choices(string.ascii_lowercase, k=rng.randint(3, 8)))
        words.append(word)
        if rng.random() < 0.3:
            chars = list(word)
            rng.shuffle(chars)
            words.append("".join(chars))

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", encoding="utf-8", delete=False
    ) as f:
        f.write("\n".join(words))
        path = f.name

    try:
        naive_result = {frozenset(g) for g in naive(path)}

        external(path)
        external_result = _parse_stdout(capsys.readouterr().out)

        assert external_result == naive_result
    finally:
        os.unlink(path)
