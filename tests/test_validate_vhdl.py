import pytest

from io_gen import ValidationError
from io_gen.tables.signal_table import build_signal_table, SignalTable
from io_gen.validate import validate_vhdl


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


# ---------------------------------------------------------------------------
# Valid - should not raise
# ---------------------------------------------------------------------------

def test_all_valid() -> None:
    """All signal names, auto-generated instance names, and top are valid identifiers."""
    st = _make_signal_table(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
            }
        ]
    )
    validate_vhdl(st, "my_top")


def test_bypass_skips_instance_check() -> None:
    """Bypass signals have instance=None and must not cause a crash or false failure."""
    st = _make_signal_table(
        [
            {
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            }
        ]
    )
    validate_vhdl(st, "my_top")


def test_valid_instance_override() -> None:
    """A user-supplied instance override that is a valid identifier passes."""
    st = _make_signal_table(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
                "instance": "clk_buf",
            }
        ]
    )
    validate_vhdl(st, "my_top")


def test_bypass_and_normal_signal_both_valid() -> None:
    """Mix of bypass and normal signals all passing validation."""
    st = _make_signal_table(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
            },
            {
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
        ]
    )
    validate_vhdl(st, "my_top")


# ---------------------------------------------------------------------------
# Invalid top name
# ---------------------------------------------------------------------------

INVALID_TOP_CASES = [
    ("top_starts_with_digit", "0top"),
    ("top_has_hyphen", "my-top"),
    ("top_empty_string", ""),
    ("top_leading_underscore", "_my_top"),
    ("top_trailing_underscore", "my_top_"),
    ("top_consecutive_underscores", "my__top"),
]


@pytest.mark.parametrize(
    "top",
    [pytest.param(t, id=label) for label, t in INVALID_TOP_CASES],
)
def test_invalid_top_raises(top: str) -> None:
    """An invalid top entity name raises ValidationError."""
    st = _make_signal_table(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
            }
        ]
    )
    with pytest.raises(ValidationError):
        validate_vhdl(st, top)


# ---------------------------------------------------------------------------
# Invalid signal name
# ---------------------------------------------------------------------------

INVALID_SIGNAL_NAME_CASES = [
    ("signal_name_starts_with_digit", "0clk"),
    ("signal_name_has_hyphen", "sys-clk"),
    ("signal_name_leading_underscore", "_sys_clk"),
    ("signal_name_trailing_underscore", "sys_clk_"),
    ("signal_name_consecutive_underscores", "sys__clk"),
]


@pytest.mark.parametrize(
    "name",
    [pytest.param(n, id=label) for label, n in INVALID_SIGNAL_NAME_CASES],
)
def test_invalid_signal_name_raises(name: str) -> None:
    """An invalid signal name raises ValidationError."""
    st = _make_signal_table(
        [
            {
                "name": name,
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
            }
        ]
    )
    with pytest.raises(ValidationError):
        validate_vhdl(st, "my_top")


def test_bypass_signal_invalid_name_raises() -> None:
    """An invalid signal name on a bypass signal raises ValidationError.

    Bypass signals still produce top-level ports and XDC constraints, so
    their name is used as an HDL identifier and must be validated.
    """
    st = _make_signal_table(
        [
            {
                "name": "0spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            }
        ]
    )
    with pytest.raises(ValidationError):
        validate_vhdl(st, "my_top")


# ---------------------------------------------------------------------------
# Invalid instance name override
# ---------------------------------------------------------------------------

INVALID_INSTANCE_CASES = [
    ("instance_starts_with_digit", "0inst"),
    ("instance_has_hyphen", "bad-inst"),
    ("instance_leading_underscore", "_clk_buf"),
    ("instance_trailing_underscore", "clk_buf_"),
    ("instance_consecutive_underscores", "clk__buf"),
]


@pytest.mark.parametrize(
    "instance",
    [pytest.param(i, id=label) for label, i in INVALID_INSTANCE_CASES],
)
def test_invalid_instance_override_raises(instance: str) -> None:
    """A user-supplied instance name that is an invalid identifier raises ValidationError."""
    st = _make_signal_table(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
                "instance": instance,
            }
        ]
    )
    with pytest.raises(ValidationError):
        validate_vhdl(st, "my_top")
