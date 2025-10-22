from pathlib import Path
from typing import Any
import json


def strip_line_endings(line: str) -> str:
    """Strips all line endings from a string"""
    s = line.replace("\r\n", "\n").replace("\r", "\n")
    return s.rstrip("\n")


def read_golden_lines(path: str | Path) -> list[str]:
    """Reads a file into logical lines without any line termination characgters"""
    with open(path, "r", encoding="utf-8", newline="") as lines:
        golden_lines = [strip_line_endings(line) for line in lines]
    return golden_lines


def read_vhdl_signals(path: str | Path) -> list[dict[str, Any]]:
    """Reads a JSON file containing data that will determine VHDL signals definitions"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]
