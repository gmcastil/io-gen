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
    table.add(
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obuf_led",
        }
    )
    assert len(table) == 1


def test_add_two_signals_len_two() -> None:
    """Adding two signals produces length 2."""
    table = PinTable()
    table.add(
        {
            "name": "sys_clk",
            "pins": "G22",
            "width": 1,
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibuf_sys_clk",
        }
    )
    table.add(
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obuf_led",
        }
    )
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
# add() - instance field
# ---------------------------------------------------------------------------


def test_infer_true_produces_instance_none() -> None:
    """A signal with infer:true produces instance=None in every pin row."""
    table = PinTable()
    table.add(
        {
            "name": "sys_clk",
            "pins": "G22",
            "width": 1,
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "infer": True,
            "bypass": False,
            "comment": {},
            "instance": "ibuf_sys_clk",
        }
    )
    rows = table.table["sys_clk"]
    assert all(row["instance"] is None for row in rows)


def test_bypass_true_produces_instance_none() -> None:
    """A signal with bypass:true produces instance=None in every pin row."""
    table = PinTable()
    table.add(
        {
            "name": "spare",
            "pins": "J24",
            "width": 1,
            "direction": "out",
            "buffer": None,
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": True,
            "comment": {},
            "instance": None,
        }
    )
    rows = table.table["spare"]
    assert all(row["instance"] is None for row in rows)


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


def test_build_pin_table_signal_membership() -> None:
    """build_pin_table includes generate:true signals and excludes generate:false signals."""
    signal_table = build_signal_table(_INTEGRATION_DOC)
    pin_table = build_pin_table(signal_table)
    assert "sys_clk" in pin_table.table
    assert "led" in pin_table.table
    assert "ref_clk" in pin_table.table
    assert "reserved_nc" not in pin_table.table


def test_build_pin_table_len() -> None:
    """len(pin_table) excludes generate:false signals."""
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


# ---------------------------------------------------------------------------
# PinTable.__getitem__
# ---------------------------------------------------------------------------


def test_getitem_returns_rows_for_scalar_signal() -> None:
    """pt[name] returns the list of pin rows for a scalar signal."""
    table = PinTable()
    table.add(
        {
            "name": "sys_clk",
            "pins": "G22",
            "width": 1,
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibuf_sys_clk",
        }
    )
    rows = table["sys_clk"]
    assert isinstance(rows, list)
    assert len(rows) == 1


def test_getitem_returns_rows_for_bus_signal() -> None:
    """pt[name] returns one row per pin for a bus signal."""
    table = PinTable()
    table.add(
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obuf_led",
        }
    )
    rows = table["led"]
    assert isinstance(rows, list)
    assert len(rows) == 4


def test_getitem_missing_key_raises_key_error() -> None:
    """pt[name] raises KeyError for a signal not in the table."""
    table = PinTable()
    with pytest.raises(KeyError):
        _ = table["nonexistent"]


def test_getitem_scalar_row_contents() -> None:
    """pt[name] for a scalar returns a row with correct pin, index, and iostandard."""
    table = PinTable()
    table.add(
        {
            "name": "sys_clk",
            "pins": "G22",
            "width": 1,
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibuf_sys_clk",
        }
    )
    rows = table["sys_clk"]
    assert rows[0]["pin"] == "G22"
    assert rows[0]["index"] == 0
    assert rows[0]["iostandard"] == "LVCMOS18"
    assert rows[0]["is_bus"] is False
    assert rows[0]["instance"] == "ibuf_sys_clk_i0"


def test_getitem_bus_row_contents() -> None:
    """pt[name] for a bus returns rows with correct pin, index, and iostandard per element."""
    table = PinTable()
    table.add(
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obuf_led",
        }
    )
    rows = table["led"]
    assert rows[0]["pin"] == "A22"
    assert rows[0]["index"] == 0
    assert rows[2]["pin"] == "C22"
    assert rows[2]["index"] == 2
    assert rows[3]["instance"] == "obuf_led_i3"
    assert all(row["iostandard"] == "LVCMOS18" for row in rows)
    assert all(row["is_bus"] is True for row in rows)


def test_getitem_differential_scalar_row_contents() -> None:
    """pt[name] for a differential scalar returns a row with correct pinset and index."""
    table = PinTable()
    table.add(
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "width": 1,
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibufds_ref_clk",
        }
    )
    rows = table["ref_clk"]
    assert rows[0]["pinset"] == {"p": "H22", "n": "H23"}
    assert rows[0]["index"] == 0
    assert rows[0]["iostandard"] == "LVDS"
    assert rows[0]["is_bus"] is False
    assert rows[0]["instance"] == "ibufds_ref_clk_i0"
