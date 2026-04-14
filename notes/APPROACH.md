# Approach

## First, what does their stack tell me?

Looking at what Mediasense listed:

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, SQLAlchemy, Pandas |
| Frontend | JavaScript & React |
| Infra | Amazon Web Services, Terraform |
| Database | PostgreSQL |
| Containers | Docker |

Mediasense use both Python and JavaScript. My first instinct is to ask — which one fits this task better?

---

## Working through the language choice

They do use JavaScript, but it's scoped to the frontend — React components, UI logic. It's not doing any heavy lifting on the backend side.

Python, on the other hand, is running everything behind the scenes: the API layer (FastAPI), data processing (Pandas), database ORM (SQLAlchemy). That's where the real backend work lives.

The task I'm solving — an anagram checker — is backend logic. It's not a UI. It's not a browser feature. So reaching for JavaScript here would be solving the right problem with the wrong tool for this team.

**Python is the clear choice.**

---

## Okay, but how should I write it?

Just knowing the language isn't enough. The question now is: how do I write Python in a way that resonates with *how they actually work*?

Two directions I'm considering:

**Option A — Keep it simple**
A clean, well-named function. Handle edge cases. Write it like a senior dev on their team would.

**Option B — Go one level deeper**
Structure it so it could live inside a FastAPI service. Add input validation. Separate the logic cleanly. Make it look like a real backend feature, not a script.

Option B is more work, but it shows I'm not just solving the toy problem — I'm thinking about how this fits into their actual system.

---

## What I want to avoid

Defaulting to JavaScript without thinking. If I had just seen "they use JS" and gone with that, it would signal:

> *"I saw web tech and jumped to JS"*
> instead of
> *"I understood your architecture"*

That's the kind of thing that's hard to take back.

---

## How I'll frame the submission

When I submit, I want to make the reasoning visible — not in an over-explaining way, but enough to show the decision was intentional:

> "I implemented this in Python to align with your backend stack (FastAPI-based services), structuring it so it could slot into an API endpoint if needed."

That one sentence does a lot. It shows stack awareness, systems thinking, and that I treated this as more than a puzzle to solve.

---

## Where I landed

Starting without the full stack picture, Python already felt like the safer bet. Now that I can see the full picture — it's not just safe, it's the right call.

---

## What happens when the file doesn't fit in memory?

The naive solution works well for reasonably sized files. But what if the file is enormous — say, hundreds of gigabytes? The `groups` dictionary grows alongside the file. At some point, it runs out of memory and crashes.

So the question becomes: how do I group anagrams without holding everything in RAM at once?

The approach I'd take is an **external sort**. Here's the thinking:

1. **Transform** — stream the file line by line and emit `(signature, word)` pairs, where signature is the sorted letters (e.g. `car → acr`). This step never loads more than one line at a time.

2. **Sort** — sort all pairs by signature. Sorting can be done externally in chunks that fit in memory, then merged — this is exactly how Unix `sort` works on large files.

3. **Stream the sorted output** — once sorted, all anagrams are consecutive. Walk through them once, collect each group, and print it. Again, only one group lives in memory at a time.

```python
# Sketch of the scaled approach
import sys
from itertools import groupby


def stream_signatures(file_path):
    """Yield (signature, word) pairs without loading the full file."""
    with open(file_path, "r") as f:
        for line in f:
            word = line.strip()
            if word:
                yield "".join(sorted(word.lower())), word


def group_anagrams_at_scale(file_path):
    """Group anagrams using sort-and-stream — constant memory per group."""
    pairs = sorted(stream_signatures(file_path), key=lambda x: x[0])

    for _, group in groupby(pairs, key=lambda x: x[0]):
        words = [word for _, word in group]
        print(" ".join(words))
```

The `sorted()` call here still loads into memory for demonstration — in a true large-file scenario, you'd replace it with an external sort (writing chunks to disk, then merging). But the structure is the same: transform, sort, stream.

The key insight is that **the sort step is the only place you need to touch the whole dataset**, and sorting is a well-understood problem with mature tools for doing it off-heap.
