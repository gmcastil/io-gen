import json
from pathlib import Path
from typing import Dict

from io_gen.models import PinRow
from io_gen.models import SignalRow

from tests.helpers import pin_table_row_from_dict
from tests.helpers import signal_table_row_from_dict


def load_pin_table(path: str | Path) -> list[PinRow]:
    """Loads a properly typed `pin_table` from a JSON file

    Expects the file to contain a top-level JSON array of objects where each object is either:
        - single-ended: {..., "pin": "A17", ...}
        - differential: {..., "p": "J18", "n": "J19", ...}

    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Pin table JSON must be a top-level array of objects")

    pin_table: list[PinRow] = []
    for index, item in enumerate(data):
        if not isinstance(item, Dict):
            raise ValueError(f"Row {index} must be a JSON object")
        pin_table.append(pin_table_row_from_dict(item))

    return pin_table


def load_signal_table(path: str | Path) -> list[SignalRow]:
    """Loads a properly typed `signal_table` from a JSON file

    Expects the file to contain a top-level JSON array of objects where each element
    contains fields from the YAML schema, with the addition of the 'diff_pair'
    and 'bus' Boolean values.

    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Signal table JSON must be a top-level array of objects")

    signal_table: list[SignalRow] = []
    for index, item in enumerate(data):
        if not isinstance(item, Dict):
            raise ValueError(f"Row {index} must be a JSON object")
        signal_table.append(signal_table_row_from_dict(item))

    return signal_table
