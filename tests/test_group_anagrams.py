import pytest
from group_anagrams import group_anagrams


def _as_sets(groups: list[list[str]]) -> set[frozenset[str]]:
    """Normalise group output for order-independent comparison."""
    return {frozenset(g) for g in groups}


# ---------------------------------------------------------------------------
# Correctness
# ---------------------------------------------------------------------------

def test_basic_grouping(tmp_word_file):
    path = tmp_word_file(["eat", "tea", "tan", "nat", "bat"])
    result = _as_sets(group_anagrams(path))
    assert result == {
        frozenset(["eat", "tea"]),
        frozenset(["tan", "nat"]),
        frozenset(["bat"]),
    }


def test_single_word(tmp_word_file):
    path = tmp_word_file(["hello"])
    result = group_anagrams(path)
    assert len(result) == 1
    assert result[0] == ["hello"]


def test_all_unique(tmp_word_file):
    words = ["cat", "dog", "bird"]
    path = tmp_word_file(words)
    result = _as_sets(group_anagrams(path))
    assert result == {frozenset([w]) for w in words}


def test_all_same_anagram(tmp_word_file):
    path = tmp_word_file(["eat", "tea", "ate"])
    result = group_anagrams(path)
    assert len(result) == 1
    assert frozenset(result[0]) == frozenset(["eat", "tea", "ate"])


def test_case_insensitive_grouping(tmp_word_file):
    path = tmp_word_file(["Eat", "tEa"])
    result = group_anagrams(path)
    assert len(result) == 1
    assert frozenset(result[0]) == frozenset(["Eat", "tEa"])


def test_preserves_original_case(tmp_word_file):
    path = tmp_word_file(["Eat", "Tea"])
    result = group_anagrams(path)
    flat = [w for group in result for w in group]
    assert "Eat" in flat
    assert "Tea" in flat
    assert "eat" not in flat
    assert "tea" not in flat


def test_ignores_blank_lines(tmp_word_file):
    path = tmp_word_file(["eat", "", "tea", "", "bat"])
    result = group_anagrams(path)
    flat = [w for group in result for w in group]
    assert "" not in flat
    assert len(flat) == 3


def test_unicode_words(tmp_word_file):
    path = tmp_word_file(["café", "face"])
    # Should not raise UnicodeDecodeError
    result = group_anagrams(path)
    assert any("café" in g for g in result)


# ---------------------------------------------------------------------------
# Error / edge cases
# ---------------------------------------------------------------------------

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        group_anagrams("/nonexistent/path/words.txt")


def test_empty_file(tmp_word_file):
    path = tmp_word_file([])
    with pytest.raises(ValueError):
        group_anagrams(path)


def test_whitespace_only_file(tmp_word_file):
    path = tmp_word_file(["   ", "\t", "  "])
    with pytest.raises(ValueError):
        group_anagrams(path)
