import json
from pathlib import Path
from typing import Dict

from io_gen.models import PinRow
from tests.helpers import pin_table_row_from_dict


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
