from typing import Optional, Any, Mapping

from io_gen.models import PinRow, Comment, SingleEnded, DiffPair


def normalize_comment(raw: Any) -> Optional[Comment]:
    if raw is None:
        return None
    if isinstance(raw, Mapping):
        return Comment(hdl=raw.get("hdl"), xdc=raw.get("xdc"))
    if isinstance(raw, str):
        return Comment(hdl=raw, xdc=raw)
    raise ValueError("Comment must null, string, or object with 'hdl' or 'xdc'")


def pin_table_row_from_dict(item: dict[str, Any]) -> PinRow:
    """Return a `PinRow` object from a dict. Intended to help assemble a pin table from JSON"""

    # Start by assembling the common fields for each pin table entry
    common = dict(
        name=item["name"],
        index=item.get("index"),
        direction=item["direction"],
        buffer=item["buffer"],
        width=item["width"],
        bus=item["bus"],
        iostandard=item["iostandard"],
    )

    # Convert a comment dict (or str) to Comment type
    common["comment"] = normalize_comment(item.get("comment"))

    # Now add the pin vs pinset specific details
    if "pin" in item:
        row = SingleEnded(pin=item["pin"], **common)
    elif "p" in item and "n" in item:
        row = DiffPair(p=item["p"], n=item["n"], **common)
    else:
        # This should never happen if we're just assembling test data
        raise ValueError(
            f"Row for '{item.get('name', '?')}' missing 'pin' or 'p' and 'n'."
        )
    row.validate()
    return row
