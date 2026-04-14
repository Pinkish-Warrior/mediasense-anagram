import tracemalloc
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from group_anagrams import group_anagrams as naive
from anagram_scalability import group_anagrams as scaled
from anagram_external_sort import group_anagrams as external

_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Change this to "large_words_file.txt" to see a more pronounced difference
FILE = os.path.join(_data_dir, "my_words_file.txt")


def measure(fn, file_path):
    """Run a function and return its peak memory usage in KB."""
    tracemalloc.start()
    fn(file_path)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024


# Suppress output from each function so only the summary prints
import io, sys
sink = io.StringIO()

sys.stdout = sink
naive_peak   = measure(naive,    FILE)
scaled_peak  = measure(scaled,   FILE)
external_peak = measure(external, FILE)
sys.stdout = sys.__stdout__

# Peak memory is the highest point reached during execution, not just what's left at the end
print(f"{'Approach':<20} {'Peak Memory':>12}")
print("-" * 33)
print(f"{'Naive (dict)':<20} {naive_peak:>10.2f} KB")
print(f"{'Scaled (sorted)':<20} {scaled_peak:>10.2f} KB")
print(f"{'External (Unix sort)':<20} {external_peak:>10.2f} KB")
