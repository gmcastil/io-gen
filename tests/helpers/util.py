import difflib
from pathlib import Path


def strip_line_endings(line: str) -> str:
    """Strips all line endings from a string"""
    s = line.replace("\r\n", "\n").replace("\r", "\n")
    return s.rstrip("\n")


def read_golden_lines(path: str | Path) -> list[str]:
    """Reads a file into logical lines without any line termination characgters"""
    with open(path, "r", encoding="utf-8", newline="") as lines:
        golden_lines = [strip_line_endings(line) for line in lines]
    return golden_lines


def unified_diff(
    expected: list[str], actual: list[str], fromfile="expected", tofile="actual"
) -> str:
    """Return a unified diff string or empty if equal"""

    if expected == actual:
        return ""

    return "\n".join(
        difflib.unified_diff(
            expected, actual, fromfile=fromfile, tofile=tofile, lineterm=""
        )
    )
