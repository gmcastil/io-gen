from dataclasses import dataclass

from .signal_table import SignalTable


@dataclass
class PinRow:
    pin: str
    iostandard: str
    direction: str
    buffer: str | None
    infer: bool
    instance: str | None
    is_bus: bool


@dataclass
class PinSetRow:
    pinset: dict
    iostandard: str
    direction: str
    buffer: str | None
    infer: bool
    instance: str | None
    is_bus: bool


class PinTable:

    def __init__(self) -> None:
        pass


def build_pin_table(signal_table: SignalTable) -> "PinTable":
    raise NotImplementedError
