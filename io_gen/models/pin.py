from dataclasses import dataclass

from typing import Optional, Union

from .common import Comment


@dataclass(frozen=True)
class PinRowBase:
    name: str
    index: Optional[int]
    direction: str
    buffer: str
    width: int
    bus: bool
    iostandard: str
    comment: Comment

    def validate(self) -> None:
        """
        Raise ValueError if not consistent or invalid values given

        This is not intended to override or replace schema checks or other validations that occur
        during flattening or when the signal and bank tables are created. It is intended to document
        some assumptions and serve as a final sanity check before actually emitting XDC or HDL

        Raises:
            ValueError

        """
        if not self.name:
            raise ValueError("Pin row: 'name' must be non-empty")
        if not isinstance(self.width, int) or self.width < 1:
            raise ValueError(f"{self.name}: 'width' must be >= 1")
        if not isinstance(self.bus, bool):
            raise ValueError(f"{self.name}: 'bus' must be a boolean")
        if not isinstance(self.iostandard, str) or not self.iostandard:
            raise ValueError(f"{self.name}: 'iostandard' must be a non-empty string")

        # If this is declared as a bus, it has to also have an index
        if self.bus and not isinstance(self.index, int):
            raise ValueError(
                f"{self.name}: all bus entries must have an integer 'index'"
            )

        if not self.bus and self.index is not None:
            raise ValueError(f"{self.name}: scalar entries must have 'index' = None")


@dataclass(frozen=True)
class SingleEnded(PinRowBase):
    pin: str

    def validate(self) -> None:
        super().validate()
        if not isinstance(self.pin, str) or not self.pin:
            raise ValueError(f"{self.name}: single-ended row requires non-empty 'pin'")


@dataclass(frozen=True)
class DiffPair(PinRowBase):
    p: str
    n: str

    def validate(self) -> None:
        super().validate()
        if not isinstance(self.p, str) or not self.p:
            raise ValueError(f"{self.name}: single-ended row requires non-empty 'p'")
        if not isinstance(self.n, str) or not self.n:
            raise ValueError(f"{self.name}: single-ended row requires non-empty 'n'")


PinRow = Union[SingleEnded, DiffPair]
