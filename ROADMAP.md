# Project Roadmap — mediasense-anagram

Full journey from initial implementation through external audit, phased remediation, and final assessment.

---

## Overview

```mermaid
flowchart TD
    ORIGIN["Initial Codebase"]
    AUDIT["Audit Phase"]
    PHASE1["Phase 1 — Critical Bugs"]
    PHASE2["Phase 2 — Architectural Refinements"]
    PHASE3["Phase 3 — Automated Test Suite"]
    CONCLUSION["Conclusion & Recommendations"]

    ORIGIN --> AUDIT
    AUDIT --> PHASE1
    PHASE1 --> PHASE2
    PHASE2 --> PHASE3
    PHASE3 --> CONCLUSION

    style ORIGIN    fill:#1e3a5f,stroke:#4a9eff,color:#e8f4fd
    style AUDIT     fill:#3d1a1a,stroke:#ff6b6b,color:#fde8e8
    style PHASE1    fill:#1a2d1a,stroke:#6bcf6b,color:#e8fde8
    style PHASE2    fill:#2d2a1a,stroke:#cfb86b,color:#fdf8e8
    style PHASE3    fill:#1a1a3d,stroke:#6b6bcf,color:#e8e8fd
    style CONCLUSION fill:#2d1a2d,stroke:#cf6bcf,color:#fde8fd
```

---

## Initial Codebase

```mermaid
flowchart LR
    O1["group_anagrams.py Naive dict approach"]
    O2["anagram_scalability.py Sort-based approach"]
    O3["anagram_external_sort.py Unix sort approach"]
    O4["smart_anagram.py Auto dispatcher"]
    O5["compare_memory.py Memory benchmarks"]
    O6["prove_scaling.py Scaling benchmarks"]

    style O1 fill:#1e3a5f,stroke:#4a9eff,color:#e8f4fd
    style O2 fill:#1e3a5f,stroke:#4a9eff,color:#e8f4fd
    style O3 fill:#1e3a5f,stroke:#4a9eff,color:#e8f4fd
    style O4 fill:#1e3a5f,stroke:#4a9eff,color:#e8f4fd
    style O5 fill:#1e3a5f,stroke:#4a9eff,color:#e8f4fd
    style O6 fill:#1e3a5f,stroke:#4a9eff,color:#e8f4fd
```

---

## Audit Phase

```mermaid
flowchart TD
    AUDIT_IN["AUDIT.md External audit by Manus 1.6 Lite"]

    F1["CRITICAL Subprocess: no wait, no stderr, no timeout"]
    F2["CRITICAL tracemalloc ignores subprocess RSS"]
    F3["CRITICAL Temp files leak into /tmp"]
    F4["CRITICAL No encoding=utf-8 on file reads"]
    F5["MEDIUM macOS-only RAM detection"]
    F6["MEDIUM Signature logic duplicated 3×"]
    F7["LOW No automated test suite"]

    ACTION["ACTION.md Developer response: accepted + challenged findings"]
    GAP["Gap Analysis Audit missed: encoding on open, missing __main__ guards"]
    PLAN["POST_AUDIT_PLAN.md Phased implementation plan with Definition of Done"]

    AUDIT_IN --> F1 & F2 & F3 & F4 & F5 & F6 & F7
    F1 & F2 & F3 & F4 & F5 & F6 & F7 --> ACTION
    ACTION --> GAP --> PLAN

    style AUDIT_IN fill:#3d1a1a,stroke:#ff6b6b,color:#fde8e8
    style F1 fill:#5a1a1a,stroke:#ff4444,color:#fff
    style F2 fill:#5a1a1a,stroke:#ff4444,color:#fff
    style F3 fill:#5a1a1a,stroke:#ff4444,color:#fff
    style F4 fill:#5a1a1a,stroke:#ff4444,color:#fff
    style F5 fill:#5a3a1a,stroke:#ffaa44,color:#fff
    style F6 fill:#5a3a1a,stroke:#ffaa44,color:#fff
    style F7 fill:#3a3a1a,stroke:#ffff44,color:#fff
    style ACTION fill:#3d1a1a,stroke:#ff6b6b,color:#fde8e8
    style GAP    fill:#3d1a1a,stroke:#ff6b6b,color:#fde8e8
    style PLAN   fill:#3d1a1a,stroke:#ff6b6b,color:#fde8e8
```

---

## Phase 1 — Critical Bugs

> Branch: `main` · Commit: `12fd34e`

```mermaid
flowchart LR
    P1A["anagram_external_sort.py Add stderr=PIPE wait + returncode check timeout=300s · encoding=utf-8"]
    P1B["prove_scaling.py Replace /tmp with tempfile.TemporaryDirectory Add RUSAGE_CHILDREN · __main__ guard"]
    P1C["compare_memory.py Add RUSAGE_CHILDREN child RSS column __main__ guard"]
    P1D["group_anagrams.py anagram_scalability.py Add encoding=utf-8 to all open calls"]

    style P1A fill:#1a2d1a,stroke:#6bcf6b,color:#e8fde8
    style P1B fill:#1a2d1a,stroke:#6bcf6b,color:#e8fde8
    style P1C fill:#1a2d1a,stroke:#6bcf6b,color:#e8fde8
    style P1D fill:#1a2d1a,stroke:#6bcf6b,color:#e8fde8
```

---

## Phase 2 — Architectural Refinements

> Branch: `main` · Commit: `1984856`

```mermaid
flowchart LR
    P2A["smart_anagram.py Platform guard + try/except fallback 100 MB fixed threshold for non-macOS"]
    P2B["signature.py  NEW Extract make_signature Imported by all 3 grouping scripts"]
    P2C["anagram_scalability.py Pedagogical docstring marking it as learning artifact"]

    style P2A fill:#2d2a1a,stroke:#cfb86b,color:#fdf8e8
    style P2B fill:#2d2a1a,stroke:#cfb86b,color:#fdf8e8
    style P2C fill:#2d2a1a,stroke:#cfb86b,color:#fdf8e8
```

---

## Phase 3 — Automated Test Suite

> Branch: `feat/test-suite` · Commit: `ccf7054` · PR: [Pinkish-Warrior/mediasense-anagram#1](https://github.com/Pinkish-Warrior/mediasense-anagram/pull/1)

```mermaid
flowchart TD
    T1["test_signature.py 7 tests Case normalisation, anagram identity"]
    T2["test_group_anagrams.py 11 tests Correctness, edge cases, error paths"]
    T3["test_anagram_scalability.py 9 tests Mirrors naive tests + parity assertion"]
    T4["test_anagram_external_sort.py 11 tests Correctness + subprocess failure mocks + 50k words"]
    T5["test_smart_anagram.py 7 tests Dispatcher routing, cross-platform fallback"]
    T6["test_benchmarks.py 3 tests RSS non-zero, tracemalloc underreport, peak grows with input"]

    RESULT["pytest tests/ -v 47/47 PASSED ✓ · 0.51s"]

    T1 & T2 & T3 & T4 & T5 & T6 --> RESULT

    style T1 fill:#1a1a3d,stroke:#6b6bcf,color:#e8e8fd
    style T2 fill:#1a1a3d,stroke:#6b6bcf,color:#e8e8fd
    style T3 fill:#1a1a3d,stroke:#6b6bcf,color:#e8e8fd
    style T4 fill:#1a1a3d,stroke:#6b6bcf,color:#e8e8fd
    style T5 fill:#1a1a3d,stroke:#6b6bcf,color:#e8e8fd
    style T6 fill:#1a1a3d,stroke:#6b6bcf,color:#e8e8fd
    style RESULT fill:#1a5a1a,stroke:#44ff44,color:#fff
```

---

## Conclusion & Recommendations

```mermaid
flowchart TD
    CONCLUSION["CONCLUSION.md Final post-audit assessment"]

    S1["group_anagrams.py Best for small files + API integration Returns structured data"]
    S2["anagram_external_sort.py Best for large files Streams via Unix sort ~1x file size in memory"]
    S3["smart_anagram.py Best general CLI default Auto-dispatches by file size vs RAM"]
    S4["anagram_scalability.py Learning artifact only Do not use in production Higher memory than naive"]

    R1["SHORT-TERM Fix dispatcher routing: small files → naive, not scaled"]
    R2["SHORT-TERM Move scalability script to examples/ directory"]
    R3["LONG-TERM Linux Docker validation for cross-platform tests"]
    R4["LONG-TERM FastAPI wrapper around group_anagrams.py"]
    R5["LONG-TERM GitHub Actions CI pytest on every push"]

    CONCLUSION --> S1 & S2 & S3 & S4
    S1 & S2 & S3 & S4 --> R1 & R2 & R3 & R4 & R5

    style CONCLUSION fill:#2d1a2d,stroke:#cf6bcf,color:#fde8fd
    style S1 fill:#2d1a2d,stroke:#cf6bcf,color:#fde8fd
    style S2 fill:#2d1a2d,stroke:#cf6bcf,color:#fde8fd
    style S3 fill:#2d1a2d,stroke:#cf6bcf,color:#fde8fd
    style S4 fill:#5a3a1a,stroke:#ffaa44,color:#fff
    style R1 fill:#1a0f1a,stroke:#7a3a7a,color:#fde8fd
    style R2 fill:#1a0f1a,stroke:#7a3a7a,color:#fde8fd
    style R3 fill:#1a0f1a,stroke:#7a3a7a,color:#fde8fd
    style R4 fill:#1a0f1a,stroke:#7a3a7a,color:#fde8fd
    style R5 fill:#1a0f1a,stroke:#7a3a7a,color:#fde8fd
```
