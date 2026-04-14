import sys
import subprocess
from itertools import groupby


def group_anagrams(file_path):
    """Group anagrams using Unix sort — works on files larger than available memory.

    Unlike the naive approach (dictionary in RAM) or the sorted() approach (all pairs in RAM),
    this delegates sorting to Unix sort, which processes data in chunks on disk.
    Python only ever holds one line going in and one anagram group coming out.
    """

    # Step 1: transform each word into "signature\tword" and feed into Unix sort
    sort_process = subprocess.Popen(
        ["sort"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    with open(file_path, "r") as f:
        for line in f:
            word = line.strip()
            if word:
                signature = "".join(sorted(word.lower()))
                # write one line at a time — never holds more than one word in memory
                sort_process.stdin.write(f"{signature}\t{word}\n")

    sort_process.stdin.close()

    # Step 2: stream the sorted output — Unix sort handles disk if needed
    for _, group in groupby(sort_process.stdout, key=lambda line: line.split("\t")[0]):
        words = [line.strip().split("\t")[1] for line in group]
        print(" ".join(words))


def main():
    if len(sys.argv) != 2:
        print("Usage: python anagram_external_sort.py <file_path>")
        sys.exit(1)

    group_anagrams(sys.argv[1])


if __name__ == "__main__":
    main()
