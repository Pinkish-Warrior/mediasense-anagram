import sys
import os
import tempfile
import pytest

# Make scripts/ importable from any test file
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


@pytest.fixture
def tmp_word_file():
    """Factory fixture: call it with a list of words, get back a temp file path.

    The file is written UTF-8, one word per line. All created files are removed
    automatically after the test completes, even on failure.
    """
    files = []

    def _make(words: list[str]) -> str:
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", encoding="utf-8", delete=False
        )
        f.write("\n".join(words))
        f.close()
        files.append(f.name)
        return f.name

    yield _make

    for path in files:
        if os.path.exists(path):
            os.unlink(path)
