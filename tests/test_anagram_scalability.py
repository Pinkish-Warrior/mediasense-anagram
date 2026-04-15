import pytest
from group_anagrams import group_anagrams as naive
from anagram_scalability import group_anagrams as scaled


def _parse_stdout(captured: str) -> set[frozenset[str]]:
    """Parse space-separated groups from captured stdout into a comparable set."""
    groups = set()
    for line in captured.strip().splitlines():
        words = line.strip().split()
        if words:
            groups.add(frozenset(words))
    return groups


# ---------------------------------------------------------------------------
# Correctness — mirrors test_group_anagrams.py but via stdout capture
# ---------------------------------------------------------------------------

def test_basic_grouping(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "tea", "tan", "nat", "bat"])
    scaled(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {
        frozenset(["eat", "tea"]),
        frozenset(["tan", "nat"]),
        frozenset(["bat"]),
    }


def test_single_word(tmp_word_file, capsys):
    path = tmp_word_file(["hello"])
    scaled(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset(["hello"])}


def test_all_unique(tmp_word_file, capsys):
    words = ["cat", "dog", "bird"]
    path = tmp_word_file(words)
    scaled(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset([w]) for w in words}


def test_all_same_anagram(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "tea", "ate"])
    scaled(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset(["eat", "tea", "ate"])}


def test_case_insensitive_grouping(tmp_word_file, capsys):
    path = tmp_word_file(["Eat", "tEa"])
    scaled(path)
    result = _parse_stdout(capsys.readouterr().out)
    assert result == {frozenset(["Eat", "tEa"])}


def test_preserves_original_case(tmp_word_file, capsys):
    path = tmp_word_file(["Eat", "Tea"])
    scaled(path)
    out = capsys.readouterr().out
    assert "Eat" in out
    assert "Tea" in out
    assert "eat" not in out
    assert "tea" not in out


def test_ignores_blank_lines(tmp_word_file, capsys):
    path = tmp_word_file(["eat", "", "tea", "", "bat"])
    scaled(path)
    result = _parse_stdout(capsys.readouterr().out)
    flat = [w for g in result for w in g]
    assert "" not in flat
    assert len(flat) == 3


# ---------------------------------------------------------------------------
# Parity with naive
# ---------------------------------------------------------------------------

def test_output_matches_naive(tmp_word_file, capsys):
    words = ["eat", "tea", "tan", "nat", "bat", "arc", "car", "listen", "silent"]
    path = tmp_word_file(words)

    naive_result = {frozenset(g) for g in naive(path)}

    scaled(path)
    scaled_result = _parse_stdout(capsys.readouterr().out)

    assert scaled_result == naive_result
