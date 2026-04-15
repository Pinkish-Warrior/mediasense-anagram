import tracemalloc
import resource
import platform
import tempfile
import io
import sys
import os
import random
import string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from group_anagrams import group_anagrams as naive
from anagram_external_sort import group_anagrams as external


def _child_rss_kb() -> float:
    """Return cumulative peak RSS of all terminated child processes in KB."""
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    # macOS reports ru_maxrss in bytes; Linux reports in KB
    scale = 1024 if platform.system() == "Darwin" else 1
    return usage.ru_maxrss / scale


def generate_word(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def generate_anagram(word: str) -> str:
    chars = list(word)
    random.shuffle(chars)
    return "".join(chars)


def generate_temp_file(num_words: int, path: str) -> None:
    """Write num_words words to path, with ~30% anagram duplicates."""
    words = []
    for _ in range(num_words):
        word = generate_word(random.randint(3, 10))
        words.append(word)
        if random.random() < 0.3:
            words.append(generate_anagram(word))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(words))


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


SIZES = [1_000, 10_000, 50_000, 100_000, 200_000]


if __name__ == "__main__":
    header = f"{'Words':<12} {'Naive heap':>12} {'Ext heap':>10} {'Ext child RSS':>14} {'Ext total':>10}"
    print(header)
    print("-" * len(header))

    with tempfile.TemporaryDirectory() as tmpdir:
        for size in SIZES:
            path = os.path.join(tmpdir, f"words_{size}.txt")
            generate_temp_file(size, path)

            naive_heap, _ = measure(naive, path)
            ext_heap, ext_child = measure(external, path)
            ext_total = ext_heap + ext_child

            print(
                f"{size:<12,} "
                f"{naive_heap:>10.2f} KB "
                f"{ext_heap:>8.2f} KB "
                f"{ext_child:>12.2f} KB "
                f"{ext_total:>8.2f} KB"
            )
