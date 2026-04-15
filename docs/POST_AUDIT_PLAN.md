# Post-Audit Implementation Plan: mediasense-anagram

**Basis:** AUDIT.md + ACTION.md + gap analysis  
**Goal:** Elevate the project from Proof of Concept to Production Ready  
**Constraint:** Python Standard Library only (no `psutil` or other external deps)

---

## Phase 1 — Critical Bugs (High Priority)

These are objective defects that can cause data loss, zombie processes, or silently wrong output. Fix before any other work.

---

### 1.1 Subprocess Lifecycle — `scripts/anagram_external_sort.py`

**Current state (lines 15–20):**
```python
sort_process = subprocess.Popen(
    ["sort"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)
```
No `stderr`, no `wait()`, no return code check, no timeout. If `sort` fails (e.g. disk full), Python receives a `BrokenPipeError` or silently produces truncated output.

**Required changes:**
- Add `stderr=subprocess.PIPE` to `Popen`
- After consuming `stdout`, call `sort_process.wait(timeout=300)`
- Check `sort_process.returncode` — raise `RuntimeError` if non-zero
- Capture and surface `sort_process.stderr.read()` in the error message
- Add explicit `encoding="utf-8"` to replace the implicit system default

**Target result:**
```python
sort_process = subprocess.Popen(
    ["sort"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8"
)
# ... write + close stdin ...
# ... consume stdout ...
sort_process.wait(timeout=300)
if sort_process.returncode != 0:
    raise RuntimeError(
        f"sort failed (exit {sort_process.returncode}): "
        f"{sort_process.stderr.read()}"
    )
```

---

### 1.2 Fix Memory Benchmarking — `scripts/prove_scaling.py` and `scripts/compare_memory.py`

**Current state:** Both scripts use `tracemalloc` exclusively. `tracemalloc` tracks only the Python heap. Memory consumed by the `sort` subprocess is completely invisible to it, making the external sort approach appear to use near-zero RAM — which is objectively false and invalidates the project's central comparison table.

**Required changes:**
- After each call that spawns a subprocess, read peak RSS of child processes via:
  ```python
  import resource
  resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
  ```
- On macOS, `ru_maxrss` is in bytes. On Linux, it is in kilobytes — normalise accordingly:
  ```python
  import platform
  scale = 1 if platform.system() == "Linux" else 1024
  child_peak_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / scale
  ```
- Report **combined** peak: `tracemalloc` peak (Python heap) + child RSS for approaches that use subprocesses; `tracemalloc` alone for pure-Python approaches.
- Label columns clearly: `Python Heap (KB)` / `Child RSS (KB)` / `Total (KB)`

---

### 1.3 Temporary File Cleanup — `scripts/prove_scaling.py`

**Current state (lines 25–35):** Files are written to `/tmp/words_{num_words}.txt` and never deleted. Repeated runs accumulate files on disk silently.

**Required changes:**
- Replace the manual `/tmp` path with `tempfile.TemporaryDirectory()` as a context manager
- All file generation and measurement happens inside the `with` block — cleanup is automatic even on exception

```python
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    for size in SIZES:
        path = os.path.join(tmpdir, f"words_{size}.txt")
        generate_temp_file(size, path)  # pass path as argument
        # ... measure ...
```

---

### 1.4 Encoding in File Reads — `scripts/group_anagrams.py`, `scripts/anagram_scalability.py`, `scripts/anagram_external_sort.py`

**Current state:** All `open(file_path, "r")` calls omit `encoding=`. Python defaults to the system locale, which varies by OS and environment. A file written as UTF-8 on one machine may fail silently or raise `UnicodeDecodeError` on another.

**Required changes:**
- Add `encoding="utf-8"` to every `open()` call across all three scripts
- Add `encoding="utf-8"` to subprocess `Popen` (covered in 1.1)

---

## Phase 2 — Architectural Refinements (Medium Priority)

---

### 2.1 Cross-Platform RAM Detection — `scripts/smart_anagram.py`

**Current state (lines 15–25):** `get_available_ram()` uses `sysctl` and `vm_stat` — macOS-only. Crashes immediately on Linux or Windows.

**Required changes — Graceful Degradation (no external deps):**
```python
FALLBACK_RAM_BYTES = 100 * 1024 * 1024  # 100 MB safe default

def get_available_ram() -> int:
    """Return available RAM in bytes. Falls back to a safe fixed value on non-macOS."""
    import platform
    if platform.system() != "Darwin":
        print(
            "  WARNING: RAM detection is macOS-only. "
            f"Using fixed threshold of {FALLBACK_RAM_BYTES // (1024**2)} MB.",
            file=sys.stderr
        )
        return FALLBACK_RAM_BYTES
    try:
        page_size = int(subprocess.check_output(["sysctl", "-n", "hw.pagesize"]))
        vm_stat = subprocess.check_output(["vm_stat"]).decode()
        for line in vm_stat.splitlines():
            if "Pages free" in line:
                free_pages = int(line.split(":")[1].strip().rstrip("."))
                return free_pages * page_size
        total = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]))
        return int(total * 0.20)
    except (subprocess.CalledProcessError, ValueError, OSError):
        print(
            "  WARNING: RAM detection failed. "
            f"Using fixed threshold of {FALLBACK_RAM_BYTES // (1024**2)} MB.",
            file=sys.stderr
        )
        return FALLBACK_RAM_BYTES
```

---

### 2.2 Extract Shared Signature Utility — new `scripts/signature.py`

**Current state:** `"".join(sorted(word.lower()))` is duplicated verbatim in:
- `scripts/group_anagrams.py` line 24
- `scripts/anagram_scalability.py` line 11
- `scripts/anagram_external_sort.py` line 26

**Required changes:**
- Create `scripts/signature.py`:
  ```python
  def make_signature(word: str) -> str:
      """Return the canonical anagram key for a word."""
      return "".join(sorted(word.lower()))
  ```
- Replace all three inline occurrences with `from signature import make_signature`

---

### 2.3 `__main__` Guard — `scripts/compare_memory.py` and `scripts/prove_scaling.py`

**Current state:** Both scripts execute benchmark code at module level (top-level statements outside any function). Importing them as modules — which the test suite will need to do — triggers immediate execution.

**Required changes:**
- Wrap all benchmark execution in `if __name__ == "__main__":` in both files
- Extract measurement logic into named functions so tests can call them without running the full benchmark

---

### 2.4 Document Pedagogical Intent — `scripts/anagram_scalability.py`

**Current state:** No indication that this approach is a learning artifact, not the recommended production choice.

**Required changes:**
- Update the module-level docstring to state explicitly:
  > "This implementation is a learning artifact demonstrating the evolution from the naive dictionary approach toward the external sort approach. For large datasets, prefer `anagram_external_sort.py`."

---

## Phase 3 — Automated Test Suite (was "Low Priority" — elevated)

ACTION.md targets "Production Ready." That claim cannot stand without a test suite. Tests are the only mechanism that verifies correctness across all three implementations and catches regressions when changes are made.

---

### 3.1 Structure

```
tests/
├── conftest.py              # shared fixtures (tmp files, known word sets)
├── test_group_anagrams.py   # naive approach
├── test_anagram_scalability.py
├── test_anagram_external_sort.py
├── test_smart_anagram.py
├── test_signature.py        # shared utility
└── test_benchmarks.py       # memory measurement sanity checks
```

Run with: `python -m pytest tests/ -v`  
No external dependencies beyond `pytest` (stdlib `unittest` is acceptable if strictly required).

---

### 3.2 `tests/conftest.py` — Shared Fixtures

```python
import pytest
import os
import tempfile


@pytest.fixture
def tmp_word_file():
    """Return a factory that writes words to a temp file and cleans up."""
    files = []

    def _make(words: list[str]) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                        encoding="utf-8", delete=False)
        f.write("\n".join(words))
        f.close()
        files.append(f.name)
        return f.name

    yield _make

    for path in files:
        if os.path.exists(path):
            os.unlink(path)
```

---

### 3.3 `tests/test_signature.py`

| Test | Input | Expected |
|---|---|---|
| Basic word | `"eat"` | `"aet"` |
| Uppercase | `"EAT"` | `"aet"` |
| Mixed case | `"Listen"` | `"eilnst"` |
| Single char | `"a"` | `"a"` |
| Anagram pair produces same key | `"eat"`, `"tea"` | identical output |

---

### 3.4 `tests/test_group_anagrams.py` — Naive Approach

**Correctness cases:**

| Test | Description |
|---|---|
| `test_basic_grouping` | `["eat","tea","tan","nat","bat"]` → 3 groups, each group is a set match |
| `test_single_word` | One word → one group containing that word |
| `test_all_unique` | No anagram pairs → each word is its own group |
| `test_all_same_anagram` | `["eat","tea","ate"]` → one group of 3 |
| `test_case_insensitive` | `["Eat","tEa"]` → one group |
| `test_preserves_original_case` | Input `"Eat"` appears in output as `"Eat"`, not lowercased |
| `test_ignores_blank_lines` | File with blank lines between words → blank lines not included in output |
| `test_unicode_words` | Words with accented characters are processed without `UnicodeDecodeError` |

**Error / edge cases:**

| Test | Expected behaviour |
|---|---|
| `test_file_not_found` | Raises `FileNotFoundError` |
| `test_empty_file` | Raises `ValueError` |
| `test_whitespace_only_file` | Raises `ValueError` |

---

### 3.5 `tests/test_anagram_scalability.py` — Scaled Approach

Apply the same correctness cases as 3.4. The output format (words space-separated, one group per line printed to stdout) is identical, so tests should capture stdout using `capsys` and compare parsed groups as sets.

Additional test:

| Test | Description |
|---|---|
| `test_output_matches_naive` | For a known word list, assert that sorted groups from scaled == sorted groups from naive |

---

### 3.6 `tests/test_anagram_external_sort.py` — External Sort Approach

Apply the same correctness cases. Because this approach uses a subprocess, additionally test:

| Test | Description |
|---|---|
| `test_sort_not_available` | Mock `subprocess.Popen` to raise `FileNotFoundError` → verify clean error, not a crash |
| `test_sort_nonzero_exit` | Mock `sort_process.returncode = 1` → verify `RuntimeError` is raised with stderr content |
| `test_large_file_no_truncation` | Generate 50 000-word file, assert output group count matches naive approach |
| `test_utf8_words` | File with UTF-8 encoded words processes without encoding error |

---

### 3.7 `tests/test_smart_anagram.py` — Dispatcher

| Test | Description |
|---|---|
| `test_selects_scaled_for_small_file` | Patch `get_available_ram` to return large value → assert scaled path taken |
| `test_selects_external_for_large_file` | Patch `get_available_ram` to return small value → assert external path taken |
| `test_fallback_on_non_macos` | Patch `platform.system` to return `"Linux"` → `get_available_ram` returns fallback, no crash |
| `test_memory_error_fallback` | Patch scaled approach to raise `MemoryError` → assert external approach runs |

---

### 3.8 `tests/test_benchmarks.py` — Memory Measurement Sanity

These are not performance benchmarks — they verify the measurement infrastructure is correct.

| Test | Description |
|---|---|
| `test_child_rss_nonzero_for_external` | After running external sort on a real file, assert `RUSAGE_CHILDREN.ru_maxrss > 0` |
| `test_tracemalloc_alone_underreports` | Assert that `tracemalloc` peak for external sort < combined (tracemalloc + child RSS) peak — confirming the old benchmark was wrong |
| `test_naive_peak_grows_with_input` | Run naive on 1 000 and 10 000 words — assert larger input produces larger peak |

---

## Summary Table

| # | File(s) | Change | Phase |
|---|---|---|---|
| 1.1 | `anagram_external_sort.py` | Add stderr, wait(), returncode check, timeout, encoding | 1 |
| 1.2 | `prove_scaling.py`, `compare_memory.py` | Replace `tracemalloc`-only with combined tracemalloc + `RUSAGE_CHILDREN` | 1 |
| 1.3 | `prove_scaling.py` | Replace `/tmp` manual paths with `tempfile.TemporaryDirectory()` | 1 |
| 1.4 | `group_anagrams.py`, `anagram_scalability.py`, `anagram_external_sort.py` | Add `encoding="utf-8"` to all `open()` calls | 1 |
| 2.1 | `smart_anagram.py` | Wrap `get_available_ram()` in platform guard + try-except with fallback | 2 |
| 2.2 | new `signature.py` | Extract `make_signature()` utility; update all 3 scripts to import it | 2 |
| 2.3 | `compare_memory.py`, `prove_scaling.py` | Wrap top-level execution in `if __name__ == "__main__":` | 2 |
| 2.4 | `anagram_scalability.py` | Update docstring to declare pedagogical intent | 2 |
| 3.x | new `tests/` directory | Full pytest suite (signature, naive, scaled, external, dispatcher, benchmarks) | 3 |

---

## Definition of Done

### Phase 1 — Critical Bugs
- [✅] `anagram_external_sort.py` — `stderr`, `wait()`, `returncode` check, timeout added *(2026-04-15)*
- [✅] `prove_scaling.py` + `compare_memory.py` — `RUSAGE_CHILDREN` child RSS measured and reported alongside `tracemalloc` *(2026-04-15)*
- [✅] `prove_scaling.py` — `/tmp` manual paths replaced with `tempfile.TemporaryDirectory()` *(2026-04-15)*
- [✅] `group_anagrams.py`, `anagram_scalability.py`, `anagram_external_sort.py` — `encoding="utf-8"` on all `open()` calls and `Popen` *(2026-04-15)*

### Phase 2 — Architectural Refinements
- [✅] `smart_anagram.py` — `get_available_ram()` wrapped in platform guard + `try/except` with 100 MB fallback *(2026-04-15)*
- [✅] `scripts/signature.py` created — `make_signature()` extracted and imported by all three grouping scripts *(2026-04-15)*
- [✅] `compare_memory.py`, `prove_scaling.py` — top-level execution wrapped in `if __name__ == "__main__":` *(2026-04-15)*
- [✅] `anagram_scalability.py` — docstring updated to declare pedagogical intent and recommend `anagram_external_sort.py` for production *(2026-04-15)*

### Phase 3 — Automated Test Suite
- [ ] `tests/conftest.py` — shared `tmp_word_file` fixture
- [ ] `tests/test_signature.py` — 5 cases covering basic, case, and anagram-pair identity
- [ ] `tests/test_group_anagrams.py` — 11 cases (correctness + error/edge)
- [ ] `tests/test_anagram_scalability.py` — correctness parity with naive + output match assertion
- [ ] `tests/test_anagram_external_sort.py` — correctness + subprocess failure paths + UTF-8
- [ ] `tests/test_smart_anagram.py` — dispatcher routing + non-macOS fallback + MemoryError fallback
- [ ] `tests/test_benchmarks.py` — child RSS non-zero, tracemalloc underreport confirmed, peak grows with input
- [ ] `pytest tests/ -v` passes with 0 failures on macOS
