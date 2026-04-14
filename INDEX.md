# Documentation Index

## Anagram Grouper — Full Documentation

---

### 1. [README.md](README.md) — Getting Started
How to run the scripts, file descriptions, requirements, and how to generate test files.

- Overview of all scripts
- How to run the smart dispatcher
- How to run individual approaches
- How to run the memory benchmark
- Test file reference

---

### 2. [APPROACH.md](docs/APPROACH.md) — Technical Approach
The four stages of development and the decision logic behind the smart dispatcher.

- Stage 1: Naive dictionary approach
- Stage 2: Scaled sort-and-stream approach
- Stage 3: External Unix sort approach
- Stage 4: Smart dispatcher with threshold logic
- Mermaid workflow diagram of the dispatcher decision flow

---

### 3. [CONCLUSION.md](docs/CONCLUSION.md) — Full Trajectory
The complete story from the first implementation to the final smart solution, including every discovery along the way.

- Why small file benchmarks can mislead
- What peak memory actually measures
- Real benchmark results on a 262 MB / 30 million word file
- The 17x Python object overhead multiplier
- The 15% RAM threshold decision
- 5 key lessons learned

---

### 4. [prove_scaling.py](scripts/prove_scaling.py) — Scaling Proof Script
Runs naive vs external sort across increasing word counts (1K, 10K, 50K, 100K, 200K) and prints a side-by-side memory table showing how the two approaches diverge at scale.

```bash
python3 scripts/prove_scaling.py
```

---

### 5. [notes/](notes/) — Original Working Notes
Early thinking, stack analysis, language choice reasoning, and the task brief — kept as a record of how the solution evolved before the final implementation.

- `MEDIASENSE_ASSESSMENT.md` — the original task brief
- `APPROACH.md` — initial language and architecture reasoning
- `TRAJECTORY.md` — Mermaid diagram of the decision journey

---

## Quick Reference

| Question | Where to look |
|---|---|
| How do I run this? | [README.md](README.md) |
| How does the smart dispatcher decide? | [docs/APPROACH.md](docs/APPROACH.md) |
| Why not always use Unix sort? | [docs/CONCLUSION.md](docs/CONCLUSION.md) — *Why Small Files Lie* |
| What does peak memory mean? | [docs/CONCLUSION.md](docs/CONCLUSION.md) — *The Memory Question* |
| Why did Scaled use more memory than Naive? | [docs/CONCLUSION.md](docs/CONCLUSION.md) — *Testing at Scale* |
| What is the 15% threshold? | [docs/CONCLUSION.md](docs/CONCLUSION.md) — *The Decision* |
| How does memory grow with word count? | Run `python3 scripts/prove_scaling.py` |
| What was the original task? | [notes/MEDIASENSE_ASSESSMENT.md](notes/MEDIASENSE_ASSESSMENT.md) |
