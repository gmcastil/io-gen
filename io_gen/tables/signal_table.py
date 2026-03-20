from typing import Any
from collections.abc import Iterator
from copy import deepcopy


class SignalTable:
    def __init__(self) -> None:
        self.table = list()

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.table)

    def __len__(self) -> int:
        return len(self.table)

    def add(self, sig: dict[str, Any]) -> None:
        """Add a signal to the signal table, resolving fields as needed"""

        # Assert that the common fields exist first - name, pins or pinset, generate, and width
        assert "name" in sig
        assert "pins" in sig or "pinset" in sig
        # Assert the shape - doing this here as a way of documenting our expectations here
        if "pins" in sig:
            assert isinstance(sig["pins"], str) or isinstance(sig["pins"], list)
        elif "pinset" in sig:
            assert isinstance(sig["pinset"], dict)
            assert isinstance(sig["pinset"]["p"], str) or isinstance(
                sig["pinset"]["p"], list
            )
            assert isinstance(sig["pinset"]["n"], str) or isinstance(
                sig["pinset"]["n"], list
            )

        # Row entries are mixed value dicts
        row: dict[str, Any] = dict()
        # The philospohy here is that we are building up our row entry, not just
        # reassigning what came out of the YAML. Start with the common stuff
        row["name"] = sig["name"]
        if "pins" in sig:
            if isinstance(sig["pins"], str):
                # Here, width isn't requied in the schema, so we insert it
                row["width"] = 1
                row["pins"] = sig["pins"]
            else:
                # Here, width actually is required, so we grab it directly
                row["width"] = sig["width"]
                # Linter can't tell that this is list[str] so we cast it (that's why have those assertions earlier)
                row["pins"] = deepcopy(sig["pins"])
        else:
            # Linter can't identify this either, so we csat to a dict[str, obj] before we try to get the 'p' value
            if isinstance(sig["pinset"]["p"], str):
                row["width"] = 1
                row["pinset"] = deepcopy(sig["pinset"])
            else:
                row["width"] = sig["width"]
                row["pinset"] = deepcopy(sig["pinset"])

        # The schema gives this as a default, but can't enforce it
        row["generate"] = sig.get("generate", True)
        # For rows that aren't going to be generated, we have all of the required keys and none of what isn't allowed,
        # so we're done if we aren't generating this row
        if not row["generate"]:
            self.table.append(row)
            return

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

        # Consruct the instance name that everything in the IO ring will use later, if we're not bypassing
        if row["bypass"]:
            row["instance"] = None
        else:
            row["instance"] = sig.get("instance", f"{row['buffer']}_{row['name']}")

        self.table.append(row)


def signal_is_scalar(sig: dict[str, Any]) -> bool:
    """Returns True if signal is a scalar, otherwise False"""

    # Depending on who calls this, this might not have been validated yet
    if "pinset" in sig:
        assert type(sig["pinset"]["p"]) == type(sig["pinset"]["n"])

    # Are we dealing with a scalar or an array?
    if "pins" in sig and isinstance(sig["pins"], str):
        result = True
    elif "pinset" in sig and isinstance(sig["pinset"]["p"], str):
        result = True
    else:
        result = False

    return result


def signal_is_differential(sig: dict[str, Any]) -> bool:
    """Returns True if signal is a differential pair, otherse False"""
    return "pinset" in sig


def build_signal_table(doc: dict) -> SignalTable:
    """Add signal information from valiated input data and build the SignalTable"""

    table = SignalTable()
    signals = doc["signals"]
    for sig in signals:
        table.add(sig)

    return table
