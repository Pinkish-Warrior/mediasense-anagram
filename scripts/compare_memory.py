import tracemalloc
import resource
import platform
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from group_anagrams import group_anagrams as naive
from anagram_scalability import group_anagrams as scaled
from anagram_external_sort import group_anagrams as external

_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Change this to "large_words_file.txt" to see a more pronounced difference
FILE = os.path.join(_data_dir, "my_words_file.txt")


def _child_rss_kb() -> float:
    """Return cumulative peak RSS of all terminated child processes in KB."""
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    # macOS reports ru_maxrss in bytes; Linux reports in KB
    scale = 1024 if platform.system() == "Darwin" else 1
    return usage.ru_maxrss / scale


def measure(fn, file_path: str) -> tuple[float, float]:
    """Run fn on file_path and return (python_heap_kb, child_rss_kb).

    python_heap_kb — peak memory tracked by tracemalloc (Python heap only).
    child_rss_kb   — incremental peak RSS of child processes via RUSAGE_CHILDREN.
                     Will be 0 for pure-Python approaches that spawn no subprocesses.
    """
    sink = io.StringIO()
    sys.stdout = sink

    child_before = _child_rss_kb()
    tracemalloc.start()
    try:
        fn(file_path)
    finally:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sys.stdout = sys.__stdout__

    child_after = _child_rss_kb()

    python_heap_kb = peak / 1024
    child_rss_kb = max(0.0, child_after - child_before)
    return python_heap_kb, child_rss_kb


if __name__ == "__main__":
    results = [
        ("Naive (dict)",          measure(naive,    FILE)),
        ("Scaled (sorted)",       measure(scaled,   FILE)),
        ("External (Unix sort)",  measure(external, FILE)),
    ]

    print(f"{'Approach':<22} {'Python heap':>12} {'Child RSS':>11} {'Total':>9}")
    print("-" * 57)
    for label, (heap, child) in results:
        total = heap + child
        note = "  ← subprocess memory excluded by tracemalloc" if child > 0 else ""
        print(f"{label:<22} {heap:>10.2f} KB {child:>9.2f} KB {total:>7.2f} KB{note}")
