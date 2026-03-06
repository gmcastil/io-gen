from dataclasses import dataclass
from typing import Optional, TypedDict

from .common import Comment, StrOrList


@dataclass(frozen=True)
class PinSet:
    p: StrOrList
    n: StrOrList


@dataclass(frozen=True)
class SignalRow:
    name: str
    direction: str
    buffer: str

    diff_pair: bool
    bus: bool

    # Width of the signal needs to be provided, even for
    width: int
    iostandard: str

    # Exactly one of these needs to be defined
    pins: Optional[StrOrList] = None
    pinset: Optional[PinSet] = None

    comment: Optional[Comment] = None
    group: Optional[str] = None

    def validate(self) -> None:
        """
        Raise ValueError if not consistent or invalid values given

        This is not intended to override or replace schema chekcs or other validation that
        occur when extracting the signal table. It is intended to document some assumptions
        and serve as a final sanity check before flattening a SignalRow into a sequence of
        PinRow objects.

        Raises:
            ValueError

        """

        # Convenience function for checking properties
        def _require(cond: bool, msg: str) -> None:
            if not cond:
                raise ValueError(msg)

        # Basic fields
        _require(bool(self.name), "Signal row: 'name' must be non-empty")
        _require(
            isinstance(self.width, int) and self.width >= 1,
            "Signal row: 'width' must be >= 1",
        )
        _require(bool(self.iostandard), "Signal row: 'iostandard' must be non-empty")

        # Optional fields' types
        _require(
            self.comment is None or isinstance(self.comment, Comment),
            "Signal row: 'comment' must be a Comment or None",
        )
        _require(
            self.group is None
            or (isinstance(self.group, str) and self.group.strip() != ""),
            "Signal row: 'group' must be a non-empty string or None",
        )

        # Exactly one of pins or pinset
        has_pins = self.pins is not None
        has_pinset = self.pinset is not None
        _require(
            has_pins ^ has_pinset,
            "Signal row: exactly one of 'pins' or 'pinset' must be provided",
        )

        # Differeential pairs
        if has_pinset:
            _require(
                self.diff_pair is True,
                "Signal row: 'diff_pair' must be True when 'pinset' is provided",
            )
            _require(
                isinstance(self.pinset, PinSet), "Signal row: 'pinset' must be a PinSet"
            )
            # This throws linter warnings if we dont guard it here
            if self.pinset is not None:
                p, n = self.pinset.p, self.pinset.n
            else:
                raise ValueError("Signal row: 'pinset' must be not None")

            # Types: str or list[str]
            _require(
                isinstance(p, (str, list)) and isinstance(n, (str, list)),
                "Signal row: 'pinset.p' and 'pinset.n' must be str or list[str]",
            )

            # Scalar differential pair
            if isinstance(p, str) and isinstance(n, str):
                _require(
                    self.width == 1, "Signal row: scalar 'pinset' requires width == 1"
                )
                _require(
                    p.strip() != "" and n.strip() != "",
                    "Signal row: 'p' and 'n' must be non-empty",
                )
                _require(p != n, "Signal row: 'p' and 'n' must differ")
            # Vector differential pairs
            else:
                _require(
                    isinstance(p, list) and isinstance(n, list),
                    "Signal row: both 'pinset.p' and 'pinset.n' must be lists for vector pairs",
                )
                _require(
                    len(p) == len(n),
                    "Signal row: 'pinset.p' and 'pinset.n' must be same length",
                )
                _require(
                    len(p) == self.width,
                    "Signal row: length of pinset lists must equal 'width'",
                )

        # Single-ended pins
        else:
            _require(
                self.diff_pair is False,
                "Signal row: 'diff_pair' must be False when 'pins' is provided",
            )

            pins = self.pins
            _require(
                isinstance(pins, (str, list)),
                "Signal row: 'pins' must be str or list[str]",
            )

            # Scalar pin
            if isinstance(pins, str):
                _require(
                    self.width == 1, "Signal row: scalar 'pins' requires width == 1"
                )
                _require(
                    pins.strip() != "", "Signal row: 'pins' (scalar) must be non-empty"
                )
            # Vector pins
            elif isinstance(pins, list):
                _require(
                    len(pins) == self.width,
                    "Signal row: number of 'pins' must equal 'width'",
                )
                _require(
                    all(isinstance(x, str) and x.strip() for x in pins),
                    "Signal row: all 'pins' must be non-empty strings",
                )
                _require(
                    len(set(pins)) == len(pins),
                    "Signal row: duplicate pin names detected in 'pins'",
                )
            else:
                raise ValueError("Signal row: 'pins' must be a list or str")

        # Direction/buffer are enums elsewhere; here we just require non-empty strings
        _require(
            isinstance(self.direction, str),
            "Signal row: 'direction' must be a non-empty string",
        )
        _require(
            isinstance(self.buffer, str),
            "Signal row: 'buffer' must be a non-empty string",
        )

        # Bus flag is allowed for both scalar and vectors (scalar => treat as [0])
        _require(isinstance(self.bus, bool), "Signal row: 'bus' must be a boolean")
        _require(
            isinstance(self.diff_pair, bool),
            "Signal row: 'diff_pair' must be a boolean",
        )

        return None
