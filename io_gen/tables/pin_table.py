from .signal_table import SignalTable
from typing import Any


class PinTable:
    def __init__(self) -> None:
        self.table = dict()

    def add(self, sig: dict[str, Any]) -> None:
        self.table[sig["name"]] = _flatten_signal(sig)

    def __len__(self) -> int:
        return len(self.table)


def _flatten_signal(sig: dict[str, Any]) -> list[dict]:
    """Flattens a scalar or bus signal into a list of pin or pinset details"""

    # Before doing anything, make sure we're being passed a signal that belongs in the pin table
    assert sig["generate"]
    if "pins" in sig:
        return _flatten_pins(sig)
    else:
        return _flatten_pinset(sig)


def _flatten_pins(sig: dict[str, Any]) -> list[dict]:
    """Flattens a single-ended signal into a list of pin details"""
    assert "pins" in sig

    flat_sig = list()
    if isinstance(sig["pins"], str):
        row = {}
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
        # These are the nature of the signal
        row["is_bus"] = False
        row["index"] = 0
        # Now we deal with pins (the singleton)
        row["pin"] = sig["pins"]
        flat_sig.append(row)

    # Array single-ended signal
    else:
        # Sanity checking - shouldn't have gotten this far otherwise
        assert isinstance(sig["pins"], list)
        for index, pin in enumerate(sig["pins"]):
            row = {}
            row["iostandard"] = sig["iostandard"]
            row["direction"] = sig["direction"]
            row["buffer"] = sig["buffer"]
            row["infer"] = sig["infer"]
            # When we're not inferring or bypassing the buffer , we use the provided name
            # and the index to set the name of the component or module to be instantiated
            if not sig["infer"] and not sig["bypass"]:
                row["instance"] = f"{sig['instance']}_i{index}"
            else:
                row["instance"] = None
            row["is_bus"] = True
            row["index"] = index
            # More sanity check to make sure we're good
            assert isinstance(pin, str)
            row["pin"] = pin
            flat_sig.append(row)

    return flat_sig


def _flatten_pinset(sig: dict[str, Any]) -> list[dict]:
    """Flattens a differential signal into a list of pinset details"""
    assert "pinset" in sig

    flat_sig = list()
    if isinstance(sig["pinset"]["p"], str):
        row = {}
        row["iostandard"] = sig["iostandard"]
        row["direction"] = sig["direction"]
        row["buffer"] = sig["buffer"]
        row["infer"] = sig["infer"]
        # When we're not inferring the buffer, we use the provided name and the index to
        # set the name of the component or module to be instantiated
        if not sig["infer"] and not sig["bypass"]:
            row["instance"] = f"{sig['instance']}_i0"
        # Otherwise its just None
        else:
            row["instance"] = None
        # These are the nature of the signal
        row["is_bus"] = False
        row["index"] = 0
        row["pinset"] = {"p": sig["pinset"]["p"], "n": sig["pinset"]["n"]}
        flat_sig.append(row)
    else:
        assert isinstance(sig["pinset"]["p"], list)
        p_pins = sig["pinset"]["p"]
        n_pins = sig["pinset"]["n"]
        # Sanity check - already checked in validation
        assert len(p_pins) == len(n_pins)
        for index, (p_pin, n_pin) in enumerate(zip(p_pins, n_pins)):
            row = {}
            row["iostandard"] = sig["iostandard"]
            row["direction"] = sig["direction"]
            row["buffer"] = sig["buffer"]
            row["infer"] = sig["infer"]
            # When we're not inferring the buffer, we use the provided name and the index to
            # set the name of the component or module to be instantiated
            if not sig["infer"] and not sig["bypass"]:
                row["instance"] = f"{sig['instance']}_i{index}"
            else:
                row["instance"] = None
            row["is_bus"] = True
            row["index"] = index
            row["pinset"] = {"p": p_pin, "n": n_pin}
            flat_sig.append(row)

    return flat_sig


def build_pin_table(signal_table: SignalTable) -> PinTable:
    pin_table = PinTable()
    for sig in signal_table:
        if sig["generate"]:
            pin_table.add(sig)
    return pin_table
