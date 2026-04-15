# Anagram Grouper

Groups words from a file by their anagram signature. Three implementations are available, plus a smart dispatcher that picks the right one automatically based on file size and available RAM.

![CI](https://github.com/Pinkish-Warrior/mediasense-anagram/actions/workflows/ci.yml/badge.svg)

---

## Files

| File | Description |
|---|---|
| `group_anagrams.py` | Naive approach — dictionary in RAM, structured as pure logic with no I/O side effects so it can slot directly into a FastAPI endpoint |
| `anagram_external_sort.py` | External approach — delegates sorting to Unix `sort`, memory-efficient for large files |
| `smart_anagram.py` | Smart dispatcher — picks the right approach automatically based on file size vs available RAM |
| `signature.py` | Shared utility — `make_signature()` extracted and imported by all grouping scripts |
| `compare_memory.py` | Memory benchmark — compares peak RAM across approaches |
| `prove_scaling.py` | Scaling proof — runs naive vs external sort across increasing word counts |
| `anagram_scalability.py` | Learning artifact only — do not use in production (higher memory than naive) |

---

## Requirements

- Python 3.10+
- `pytest` (for running the test suite)
- Works on macOS and Linux. On non-macOS systems the smart dispatcher uses a fixed 100 MB RAM threshold.

```bash
pip install -r requirements.txt
```

---

## Running the scripts

### Smart dispatcher (recommended)

Automatically picks the best approach based on file size vs available RAM:

```bash
python3 scripts/smart_anagram.py <file_path>
```

Example output:
```
========================================
  File     : my_words_file.txt
  Size     : 49 B
  Free RAM : 63.6 MB
  Threshold: 9.5 MB (15% of free RAM)
========================================
  Decision : Naive (dict)
----------------------------------------
  Approach : Naive (dict)
  Peak RAM : 139.1 KB
  Time     : 0.00s
========================================
```

### Individual approaches

```bash
python3 scripts/group_anagrams.py <file_path>
python3 scripts/anagram_external_sort.py <file_path>
```

### Memory benchmark

Compares peak memory across approaches. Edit the `FILE` variable at the top of the script to choose which file to test:

```bash
python3 scripts/compare_memory.py
```

### Scaling proof

Runs naive vs external sort across increasing word counts (1K to 200K) to show how memory diverges with scale:

```bash
python3 scripts/prove_scaling.py
```

---

## Tests

47 tests across 6 modules covering correctness, edge cases, subprocess failure paths, cross-platform fallback, and memory benchmarks.

```bash
pytest tests/ -v
```

---

## Test files

| File | Size | Words |
|---|---|---|
| `my_words_file.txt` | 49 B | 9 words |
| `large_words_file.txt` | 262 MB | 30 million words |

To generate a large test file yourself, save the following as `generate_large_file.py` and run it:

```python
import random, string

random.seed(42)
target_bytes = 250 * 1024 * 1024  # 250 MB
written = 0

with open('large_words_file.txt', 'w') as f:
    while written < target_bytes:
        length = random.randint(3, 12)
        word = ''.join(random.choices(string.ascii_lowercase, k=length))
        line = word + '\n'
        f.write(line)
        written += len(line)
```

```bash
python3 generate_large_file.py
```

---

![Human Led AI Enhanced](https://img.shields.io/badge/Human%20Led-AI%20Enhanced%20with%20Claude%20Sonnet%204.6-D97757?logo=anthropic&logoColor=white)
