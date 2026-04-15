import sys
from itertools import groupby
from signature import make_signature


def stream_signatures(file_path):
    """Yield (signature, word) pairs without loading the full file."""
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word:
                yield make_signature(word), word


def group_anagrams(file_path):
    """Group anagrams using sort-and-stream — constant memory per group.

    NOTE: This is a learning artifact that demonstrates the evolution from the
    naive dictionary approach toward the external sort approach. It materialises
    all (signature, word) pairs into memory before sorting, which means it
    consumes *more* memory than the naive approach — not less. For large datasets,
    prefer anagram_external_sort.py, which delegates sorting to Unix sort and
    keeps only one line in Python memory at a time.
    """
    pairs = sorted(stream_signatures(file_path), key=lambda x: x[0])

    for _, group in groupby(pairs, key=lambda x: x[0]):
        words = [word for _, word in group]
        print(" ".join(words))


def main():
    if len(sys.argv) != 2:
        print("Usage: python anagram_scalability.py <file_path>")
        sys.exit(1)

    group_anagrams(sys.argv[1])


if __name__ == "__main__":
    main()
