import pytest

from io_gen.tables.pin_table import PinTable, build_pin_table
from io_gen.tables.signal_table import SignalTable, build_signal_table


# ---------------------------------------------------------------------------
# PinTable container behavior
# ---------------------------------------------------------------------------


def test_empty_table() -> None:
    """An empty PinTable has length zero."""
    table = PinTable()
    assert len(table) == 0


def test_len_counts_signals_not_pin_rows() -> None:
    """__len__ counts signal entries, not total pin rows - a 4-pin bus is 1."""
    table = PinTable()
    table.add({
        "name": "led",
        "pins": ["A22", "B22", "C22", "D22"],
        "width": 4,
        "direction": "out",
        "buffer": "obuf",
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": False,
        "bypass": False,
        "comment": {},
        "instance": "obuf_led",
    })
    assert len(table) == 1


def test_add_two_signals_len_two() -> None:
    """Adding two signals produces length 2."""
    table = PinTable()
    table.add({
        "name": "sys_clk",
        "pins": "G22",
        "width": 1,
        "direction": "in",
        "buffer": "ibuf",
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": False,
        "bypass": False,
        "comment": {},
        "instance": "ibuf_sys_clk",
    })
    table.add({
        "name": "led",
        "pins": ["A22", "B22", "C22", "D22"],
        "width": 4,
        "direction": "out",
        "buffer": "obuf",
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": False,
        "bypass": False,
        "comment": {},
        "instance": "obuf_led",
    })
    assert len(table) == 2


# ---------------------------------------------------------------------------
# add() - key and row count
# ---------------------------------------------------------------------------

# Each case is (name, sig, expected_row_count). sig is a fully normalized
# signal table row. expected_row_count is the number of pin rows that
# _flatten_signal must produce for that signal.

ADD_ROW_COUNT_CASES = [
    (
        "single_ended_scalar",
        {
            "name": "sys_clk",
            "pins": "G22",
            "width": 1,
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibuf_sys_clk",
        },
        1,
    ),
    (
        "single_ended_bus",
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obuf_led",
        },
        4,
    ),
    (
        "differential_scalar",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "width": 1,
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibufds_ref_clk",
        },
        1,
    ),
    (
        "differential_bus",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
            "width": 3,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obufds_lvds_data",
        },
        3,
    ),
]


@pytest.mark.parametrize(
    "sig, expected_count",
    [pytest.param(s, c, id=n) for n, s, c in ADD_ROW_COUNT_CASES],
)
def test_add_stores_under_signal_name(sig: dict, expected_count: int) -> None:
    """add() stores rows under the signal name as the key."""
    table = PinTable()
    table.add(sig)
    assert sig["name"] in table.table


@pytest.mark.parametrize(
    "sig, expected_count",
    [pytest.param(s, c, id=n) for n, s, c in ADD_ROW_COUNT_CASES],
)
def test_add_row_count(sig: dict, expected_count: int) -> None:
    """add() produces the correct number of pin rows for the signal."""
    table = PinTable()
    table.add(sig)
    assert len(table.table[sig["name"]]) == expected_count


# ---------------------------------------------------------------------------
# build_pin_table() - integration
# ---------------------------------------------------------------------------

# Full document with a mix of signal types used across integration tests.

_INTEGRATION_DOC = {
    "title": "Test",
    "part": "xc7k325tffg900-2",
    "signals": [
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        {
            "name": "reserved_nc",
            "pins": "H24",
            "generate": False,
        },
    ],
}


def test_build_pin_table_excludes_generate_false() -> None:
    """build_pin_table does not add generate:false signals to the table."""
    signal_table = build_signal_table(_INTEGRATION_DOC)
    pin_table = build_pin_table(signal_table)
    assert "reserved_nc" not in pin_table.table


def test_build_pin_table_includes_generate_true() -> None:
    """build_pin_table includes all generate:true signals."""
    signal_table = build_signal_table(_INTEGRATION_DOC)
    pin_table = build_pin_table(signal_table)
    assert "sys_clk" in pin_table.table
    assert "led" in pin_table.table
    assert "ref_clk" in pin_table.table


def test_build_pin_table_len_excludes_generate_false() -> None:
    """len(pin_table) counts only generate:true signals."""
    signal_table = build_signal_table(_INTEGRATION_DOC)
    pin_table = build_pin_table(signal_table)
    assert len(pin_table) == 3


def test_build_pin_table_bus_row_count() -> None:
    """A bus signal produces one row per pin in the pin table."""
    signal_table = build_signal_table(_INTEGRATION_DOC)
    pin_table = build_pin_table(signal_table)
    assert len(pin_table.table["led"]) == 4


def test_build_pin_table_returns_pin_table_instance() -> None:
    """build_pin_table returns a PinTable instance."""
    signal_table = build_signal_table(_INTEGRATION_DOC)
    pin_table = build_pin_table(signal_table)
    assert isinstance(pin_table, PinTable)
