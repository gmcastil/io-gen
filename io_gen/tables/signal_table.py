from typing import Any
from collections.abc import Iterator
from copy import deepcopy

from ..exceptions import ValidationError


class SignalTable:
    def __init__(self) -> None:
        self.table: list[dict[str, Any]] = []

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.table)

    def __len__(self) -> int:
        return len(self.table)

    def add(self, sig: dict[str, Any]) -> None:
        """Add a signal to the signal table, resolving fields as needed"""

        # The schema gives this as a default, but can't enforce it
        if not sig.get("generate", True):
            return

        # Row entries are mixed value dicts
        row: dict[str, Any] = {}
        # The philosophy here is that we are building up our row entry, not just
        # reassigning what came out of the YAML. Start with the common stuff
        row["name"] = sig["name"]
        if "pins" in sig:
            row["width"] = 1 if isinstance(sig["pins"], str) else sig["width"]
            row["pins"] = (
                sig["pins"] if isinstance(sig["pins"], str) else deepcopy(sig["pins"])
            )
        else:
            row["width"] = 1 if isinstance(sig["pinset"]["p"], str) else sig["width"]
            row["pinset"] = deepcopy(sig["pinset"])

        # These are required for everybody
        row["iostandard"] = sig["iostandard"]
        row["direction"] = sig["direction"]

        # These have default values in the schema but that doesn't guarantee they exist so we normalize here
        row["infer"] = sig.get("infer", False)
        row["bypass"] = sig.get("bypass", False)
        row["comment"] = sig.get("comment", {})

        # Get the buffer name if we're not bypasing (save for later, to name the instance)
        if row["bypass"]:
            row["buffer"] = None
        else:
            row["buffer"] = sig["buffer"]

        # Construct the instance name that everything in the IO ring will use later, if we're not bypassing
        if row["bypass"]:
            row["instance"] = None
        else:
            row["instance"] = sig.get("instance", f"{row['buffer']}_{row['name']}")

        self.table.append(row)

    def active(self) -> list[dict[str, Any]]:
        """Returns the signal table with only active signals (i.e., bypass == False)"""
        return [sig for sig in self.table if not sig["bypass"]]


def signal_is_scalar(sig: dict[str, Any]) -> bool:
    """Returns True if signal is a scalar, otherwise False"""

    # Depending on when this is called, the signal might not be validated yet
    if "pinset" in sig:
        if not isinstance(sig["pinset"]["p"], type(sig["pinset"]["n"])):
            raise ValidationError("pinset p and n must be the same type")

    # Are we dealing with a scalar or an array?
    if "pins" in sig and isinstance(sig["pins"], str):
        result = True
    elif "pinset" in sig and isinstance(sig["pinset"]["p"], str):
        result = True
    else:
        result = False

    return result


def signal_is_differential(sig: dict[str, Any]) -> bool:
    """Returns True if signal is a differential pair, others False"""
    return "pinset" in sig


def build_signal_table(doc: dict) -> SignalTable:
    """Add signal information from validated input data and build the SignalTable"""

    table = SignalTable()
    signals = doc["signals"]
    for sig in signals:
        table.add(sig)

    return table
