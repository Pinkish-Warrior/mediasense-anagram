import tracemalloc
import io
import sys
import os
import random
import string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from group_anagrams import group_anagrams as naive
from anagram_external_sort import group_anagrams as external


def generate_word(length):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def generate_anagram(word):
    chars = list(word)
    random.shuffle(chars)
    return "".join(chars)


def generate_temp_file(num_words):
    """Write a temporary word file with num_words words, return the path."""
    path = f"/tmp/words_{num_words}.txt"
    words = []
    for _ in range(num_words):
        word = generate_word(random.randint(3, 10))
        words.append(word)
        if random.random() < 0.3:
            words.append(generate_anagram(word))
    with open(path, "w") as f:
        f.write("\n".join(words))
    return path


def measure(fn, file_path):
    """Run a function and return its peak memory usage in KB."""
    sink = io.StringIO()
    sys.stdout = sink
    tracemalloc.start()
    fn(file_path)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    sys.stdout = sys.__stdout__
    return peak / 1024


SIZES = [1_000, 10_000, 50_000, 100_000, 200_000]

print(f"{'Words':<12} {'Naive (KB)':>12} {'External (KB)':>15}")
print("-" * 42)

for size in SIZES:
    path = generate_temp_file(size)
    naive_peak    = measure(naive,    path)
    external_peak = measure(external, path)
    print(f"{size:<12,} {naive_peak:>12.2f} {external_peak:>15.2f}")
