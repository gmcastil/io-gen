from .signal_table import SignalTable, signal_is_scalar
from typing import Any


class PinTable:
    def __init__(self) -> None:
        self.table = {}

    def add(self, sig: dict[str, Any]) -> None:
        sig_name = sig["name"]
        self.table[sig_name] = _flatten_signal(sig)

    def __len__(self) -> int:
        return len(self.table)

    def __getitem__(self, sig_name: str) -> list:
        if sig_name in self.table:
            return self.table[sig_name]
        else:
            raise KeyError(f"'{sig_name}' not found in pin table")


def _flatten_signal(sig: dict[str, Any]) -> list[dict]:
    """Flattens a signal table row into a list of pin or pinset rows."""

    # Operate on scalars and arrays (instead of pins vs pinsets)
    if signal_is_scalar(sig):
        return _flatten_scalar(sig)
    else:
        return _flatten_array(sig)


def _flatten_scalar(sig: dict[str, Any]) -> list[dict]:
    """Flattens a scalar single-ended or differential signal"""

    row: dict[str, Any] = {}
    row["iostandard"] = sig["iostandard"]
    row["direction"] = sig["direction"]
    row["buffer"] = sig["buffer"]
    row["infer"] = sig["infer"]

    # When we're not inferring or bypassing the buffer , we use the provided name
    # and the index to set the name of the component or module to be instantiated
    if not sig["infer"] and not sig["bypass"]:
        row["instance"] = f"{sig['instance']}_i0"
    # Otherwise its just None
    else:
        row["instance"] = None
    # Intrinsic to the signal
    row["is_bus"] = False
    row["index"] = 0
    # The only thing different between pins and pinsets
    if "pins" in sig:
        row["pin"] = sig["pins"]
    else:
        row["pinset"] = {"p": sig["pinset"]["p"], "n": sig["pinset"]["n"]}
    # Scalars need to be list-ified because the PinTable associates signal names with lists of pins
    return [row]


def _flatten_array(sig: dict[str, Any]) -> list[dict]:
    """Flattens single-ended or differential array signal"""

    if "pins" in sig:
        items = sig["pins"]
    else:
        p_pins = sig["pinset"]["p"]
        n_pins = sig["pinset"]["n"]
        items = zip(p_pins, n_pins)

    flat_sig = []
    for index, item in enumerate(items):
        row: dict[str, Any] = {}
        row["iostandard"] = sig["iostandard"]
        row["direction"] = sig["direction"]
        row["buffer"] = sig["buffer"]
        row["infer"] = sig["infer"]

        # When we're not inferring or bypassing the buffer , we use the provided name
        # and the index to set the name of the component or module to be instantiated
        if not sig["infer"] and not sig["bypass"]:
            row["instance"] = f"{sig['instance']}_i{index}"
        # Otherwise its just None
        else:
            row["instance"] = None
        # Intrinsic to the signal
        row["is_bus"] = True
        row["index"] = index

        if "pins" in sig:
            row["pin"] = item
        else:
            p_pin, n_pin = item
            row["pinset"] = {"p": p_pin, "n": n_pin}
        flat_sig.append(row)

    return flat_sig


def build_pin_table(signal_table: SignalTable) -> PinTable:
    pin_table = PinTable()
    for sig in signal_table:
        pin_table.add(sig)
    return pin_table


def pin_is_differential(pin: dict[str, Any]) -> bool:
    """Returns true if pin is differential others false"""
    return "pinset" in pin
