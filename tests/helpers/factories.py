from typing import Optional, Any, Mapping

from io_gen.models import PinRow, Comment, SingleEnded, DiffPair
from io_gen.models import SignalRow, PinSet


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


def signal_table_row_from_dict(item: dict[str, Any]) -> SignalRow:
    """Return a `SignalRow` object from a dict. Intended to help assemble a signal table from JSON"""

    common = dict(
        name=item["name"],
        direction=item["direction"],
        buffer=item["buffer"],
        diff_pair=item["diff_pair"],
        bus=item["bus"],
        width=item["width"],
        iostandard=item["iostandard"],
        comment=normalize_comment(item.get("comment", None)),
        group=item.get("group", None),
    )

    if "pins" in item:
        row = SignalRow(pins=item["pins"], **common)
    elif "pinset" in item:
        pinset = PinSet(p=item["pinset"]["p"], n=item["pinset"]["n"])
        row = SignalRow(pinset=pinset, **common)
    else:
        raise ValueError(
            f"Row for '{item.get('name', '?')}' missing 'pins' or 'pinset'."
        )
    row.validate()
    return row
