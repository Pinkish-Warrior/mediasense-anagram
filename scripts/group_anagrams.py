import sys
import os
from collections import defaultdict
from signature import make_signature


def group_anagrams(file_path: str) -> list[list[str]]:
    """Read words from a file and return them grouped by anagram.

    This function is intentionally kept as pure logic — no I/O side effects
    beyond reading the file — so it can be imported directly into a FastAPI
    endpoint or any other service layer.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"File is not readable: {file_path}")

    groups = defaultdict(list)

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word:
                key = make_signature(word)
                groups[key].append(word)

    if not groups:
        raise ValueError(f"No words found in file: {file_path}")

    return list(groups.values())


def main():
    if len(sys.argv) != 2:
        print("Usage: python group_anagrams.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        groups = group_anagrams(file_path)
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    for group in groups:
        print(" ".join(group))


if __name__ == "__main__":
    main()
