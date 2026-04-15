import os
import sys
import platform
import subprocess
import tracemalloc
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from group_anagrams import group_anagrams as naive
from anagram_external_sort import group_anagrams as external

THRESHOLD = 0.15  # use Unix sort if file is > 15% of available RAM


_FALLBACK_RAM_BYTES = 100 * 1024 * 1024  # 100 MB safe default for non-macOS systems


def get_available_ram() -> int:
    """Return available RAM in bytes.

    Uses macOS-specific sysctl/vm_stat on Darwin. On any other platform, or if
    detection fails, logs a warning and returns a safe fixed fallback so the
    dispatcher can still make a decision without crashing.
    """
    if platform.system() != "Darwin":
        print(
            f"  WARNING: RAM detection is macOS-only. "
            f"Using fixed threshold of {_FALLBACK_RAM_BYTES // (1024 ** 2)} MB.",
            file=sys.stderr,
        )
        return _FALLBACK_RAM_BYTES

    try:
        page_size = int(subprocess.check_output(["sysctl", "-n", "hw.pagesize"]))
        vm_stat = subprocess.check_output(["vm_stat"]).decode()
        for line in vm_stat.splitlines():
            if "Pages free" in line:
                free_pages = int(line.split(":")[1].strip().rstrip("."))
                return free_pages * page_size
        # vm_stat parsed but "Pages free" line absent — fall back to 20% of total
        total = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]))
        return int(total * 0.20)
    except (subprocess.CalledProcessError, ValueError, OSError):
        print(
            f"  WARNING: RAM detection failed. "
            f"Using fixed threshold of {_FALLBACK_RAM_BYTES // (1024 ** 2)} MB.",
            file=sys.stderr,
        )
        return _FALLBACK_RAM_BYTES


def format_bytes(n):
    if n < 1024:
        return f"{n} B"
    elif n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    else:
        return f"{n / 1024 / 1024:.1f} MB"


def run_with_stats(label, fn, file_path):
    import io
    tracemalloc.start()
    start = time.time()
    sys.stdout = io.StringIO()
    try:
        fn(file_path)
    finally:
        sys.stdout = sys.__stdout__
    elapsed = time.time() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"  Approach : {label}")
    print(f"  Peak RAM : {format_bytes(peak)}")
    print(f"  Time     : {elapsed:.2f}s")


def group_anagrams_smart(file_path):
    file_size = os.path.getsize(file_path)
    available_ram = get_available_ram()
    threshold_bytes = available_ram * THRESHOLD

    print("=" * 40)
    print(f"  File     : {file_path}")
    print(f"  Size     : {format_bytes(file_size)}")
    print(f"  Free RAM : {format_bytes(available_ram)}")
    print(f"  Threshold: {format_bytes(int(threshold_bytes))} (15% of free RAM)")
    print("=" * 40)

    if file_size < threshold_bytes:
        print(f"  Decision : Naive (dict)")
        print("-" * 40)
        try:
            run_with_stats("Naive (dict)", naive, file_path)
        except MemoryError:
            print("  ERROR: Out of memory. Falling back to Unix sort.")
            run_with_stats("External (Unix sort) [fallback]", external, file_path)
    else:
        print(f"  Decision : External (Unix sort)")
        print("-" * 40)
        try:
            run_with_stats("External (Unix sort)", external, file_path)
        except subprocess.CalledProcessError as e:
            print(f"  ERROR: Unix sort failed (exit code {e.returncode}). Cannot recover.")
            sys.exit(1)
        except OSError as e:
            print(f"  ERROR: Could not run Unix sort — {e}")
            sys.exit(1)

    print("=" * 40)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 smart_anagram.py <file_path>")
        sys.exit(1)

    group_anagrams_smart(sys.argv[1])
