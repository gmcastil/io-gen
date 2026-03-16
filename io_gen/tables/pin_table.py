from .signal_table import SignalTable


class PinTable:

    def __init__(self) -> None:
        pass


def _flatten_signal(sig: dict[str, object]) -> list[dict]:
    """Flattens a scalar or bus signal into a list of pin or pinset details"""

    # Before doing anything, make sure we're being passed a signal that belongs in the pin table
    assert sig["generate"]

    # Extract all of the common stuff first

    flat_sig = list()
    if "pins" in sig:
        


def build_pin_table(signal_table: SignalTable) -> "PinTable":
    raise NotImplementedError
