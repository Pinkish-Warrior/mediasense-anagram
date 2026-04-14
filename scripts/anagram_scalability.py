import sys
from itertools import groupby


def stream_signatures(file_path):
    """Yield (signature, word) pairs without loading the full file."""
    with open(file_path, "r") as f:
        for line in f:
            word = line.strip()
            if word:
                yield "".join(sorted(word.lower())), word


def group_anagrams(file_path):
    """Group anagrams using sort-and-stream — constant memory per group."""
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
