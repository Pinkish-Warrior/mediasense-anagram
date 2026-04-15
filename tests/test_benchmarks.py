"""Verify that the memory measurement infrastructure itself is correct.

These are not performance benchmarks — they assert properties of the
measurement tools so that the numbers reported by compare_memory.py and
prove_scaling.py can be trusted.
"""
import tracemalloc
import resource
import platform
import tempfile
import os
import io
import sys

from compare_memory import measure, _child_rss_kb
from group_anagrams import group_anagrams as naive
from anagram_external_sort import group_anagrams as external


def _make_word_file(num_words: int) -> str:
    import random, string, tempfile
    rng = random.Random(0)
    words = ["".join(rng.choices(string.ascii_lowercase, k=5)) for _ in range(num_words)]
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False)
    f.write("\n".join(words))
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# Child RSS is non-zero after external sort runs
# ---------------------------------------------------------------------------

def test_child_rss_nonzero_for_external():
    """After running external sort, the OS-level child RSS must be > 0.

    ru_maxrss under RUSAGE_CHILDREN is cumulative across the process lifetime,
    so we read it after the sort runs and assert it is positive — not a delta.
    """
    path = _make_word_file(5_000)
    try:
        sink = io.StringIO()
        sys.stdout = sink
        external(path)
        sys.stdout = sys.__stdout__

        scale = 1024 if platform.system() == "Darwin" else 1
        child_rss_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / scale
        assert child_rss_kb > 0, (
            f"Child RSS should be > 0 after sort subprocess; got {child_rss_kb} KB"
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# tracemalloc alone underreports for external sort
# ---------------------------------------------------------------------------

def test_tracemalloc_underreports_external_sort():
    """The combined total (tracemalloc + child RSS) must exceed tracemalloc alone.

    This confirms that tracemalloc would give a misleading lower number if used
    in isolation — the subprocess memory is only visible via RUSAGE_CHILDREN.
    """
    path = _make_word_file(5_000)
    try:
        sink = io.StringIO()
        sys.stdout = sink
        tracemalloc.start()
        external(path)
        _, tracemalloc_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sys.stdout = sys.__stdout__

        tracemalloc_kb = tracemalloc_peak / 1024

        scale = 1024 if platform.system() == "Darwin" else 1
        child_rss_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / scale

        combined_kb = tracemalloc_kb + child_rss_kb
        assert combined_kb > tracemalloc_kb, (
            f"Combined ({combined_kb:.1f} KB) should exceed tracemalloc alone "
            f"({tracemalloc_kb:.1f} KB) — child RSS was {child_rss_kb:.1f} KB"
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Naive approach memory grows with input size
# ---------------------------------------------------------------------------

def test_naive_peak_grows_with_input():
    small_path = _make_word_file(500)
    large_path = _make_word_file(10_000)
    try:
        small_heap, _ = measure(naive, small_path)
        large_heap, _ = measure(naive, large_path)
        assert large_heap > small_heap, (
            f"Expected larger input to use more memory: "
            f"small={small_heap:.1f} KB, large={large_heap:.1f} KB"
        )
    finally:
        os.unlink(small_path)
        os.unlink(large_path)
