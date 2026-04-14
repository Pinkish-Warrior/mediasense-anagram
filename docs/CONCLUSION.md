# Conclusion: From Naive to Smart

## Where We Started

The task was simple: group words from a file by their anagram signature. The first solution was the most natural one — a Python dictionary where each key is a sorted version of a word and the value is a list of matching words.

It worked. On a 9-word file it ran instantly and used 139 KB of memory. No reason to look further — until the question came up: *what happens with a much bigger file?*

---

## The Memory Question

Before testing anything large, we looked at how memory was being measured. The benchmark tool (`compare_memory.py`) used Python's `tracemalloc`, specifically `get_traced_memory()` which returns two values:

- **current** — memory allocated right now
- **peak** — the highest point reached at any moment during execution

This matters because memory can be freed before a function returns. Peak tells the real story — it captures spikes that would have already disappeared by the time you check.

On a 9-word file, all three approaches looked similar:

| Approach | Peak Memory |
|---|---|
| Naive (dict) | 139.28 KB |
| Scaled (sorted) | 138.90 KB |
| External (Unix sort) | 397.44 KB |

External sort actually looked *worse* here. That was the first surprise — and the first lesson.

---

## Why Small Files Lie

Unix sort had more overhead on a small file because spawning a subprocess and buffering its output through a pipe costs more than just building a tiny dictionary. The advantage of external sort only appears when the file is large enough that Python's in-memory structures become the bottleneck.

This is the crossover point: **when the file approaches your available RAM, Python's object overhead becomes the problem.**

A Python string is not just its characters. It carries object metadata, reference counts, and hash values. A list of strings in a dictionary carries even more. A 262 MB flat file can explode to 4+ GB in memory once Python wraps every word in its object model.

---

## Testing at Scale

To see this in practice, we generated a 262 MB file with 30 million random words and ran the same benchmark.

The results were decisive:

| Approach | Peak Memory | vs File Size | Outcome |
|---|---|---|---|
| Naive (dict) | 4,412 MB | 17x | Completed |
| Scaled (sorted) | 5,451 MB | 21x | Completed |
| External (Unix sort) | 275 MB | ~1x | Completed |

Scaled was actually the worst of the three — not better than Naive. It builds all `(signature, word)` pairs as tuples in memory before calling `sorted()`, which adds tuple and list overhead on top of what the dictionary approach already needs. Both Python approaches used over half the machine's total RAM.

External sort peaked at 275 MB — roughly the size of the file itself. Unix `sort` never loads everything into memory at once. It reads in chunks, sorts them, writes intermediate results to disk, and merges them. Python's role was reduced to a thin pipe: feed one word in, read one group out.

---

## The Real Cost of Python Objects

The gap between 262 MB (file size) and 4,412 MB (naive peak) is a 17x multiplier — and Scaled made it worse at 21x. That is Python object overhead at work:

- Every string has a fixed-size object header (~50 bytes on CPython)
- Every list entry is a pointer (8 bytes)
- Every dictionary key and value adds hash storage and bucket overhead
- The garbage collector tracks all of it

Unix `sort` sees none of this. It treats the data as raw bytes, never materialises a Python object, and lets the OS manage memory paging.

---

## The Decision

With real numbers in hand, the right approach became clear:

- **Small file** (fits comfortably in RAM) → use Scaled (sorted). It is faster, no subprocess overhead, no pipe buffering.
- **Large file** (approaches available RAM) → use External (Unix sort). It is the only approach that can finish.

The threshold we settled on: **15% of available free RAM**. If the file is smaller than that, the Python approach has plenty of headroom. If it is larger, hand it off to Unix sort.

---

## The Result: `smart_anagram.py`

The smart dispatcher reads the file size and available RAM at runtime and makes the decision automatically. It prints exactly why it chose what it chose, how much memory was used, and how long it took.

```
========================================
  File     : large_words_file.txt
  Size     : 250.0 MB
  Free RAM : 67.7 MB
  Threshold: 10.2 MB (15% of free RAM)
========================================
  Decision : External (Unix sort)
----------------------------------------
  Approach : External (Unix sort)
  Peak RAM : 275.0 MB
  Time     : 41.83s
========================================
```

It also includes a safety net: if the scaled approach runs unexpectedly out of memory (e.g. the system was already under pressure when the threshold was calculated), it catches the `MemoryError` and falls back to Unix sort automatically.

---

## What This Journey Taught

1. **Benchmarks on small inputs can mislead.** Unix sort looked worse on 9 words. At 30 million words it used 20x less memory.
2. **Peak memory is what matters, not final memory.** An approach can free everything before returning and still have spiked your system at its worst moment.
3. **Python object overhead is significant.** A 262 MB file became 4–5 GB in RAM. Never assume memory scales linearly with file size when Python data structures are involved.
4. **"Improved" does not always mean better.** Scaled looked like a refinement of Naive but used more memory — the tuple pairs added overhead on top of what the dictionary already needed.
5. **The right tool depends on context.** There is no single best approach — only the best approach for a given file size and available RAM. The smart dispatcher makes that decision explicit and automatic.
