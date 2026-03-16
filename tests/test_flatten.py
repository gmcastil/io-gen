import pytest

from io_gen.tables.pin_table import _flatten_signal


# ---------------------------------------------------------------------------
# Full row shape - single-ended
# ---------------------------------------------------------------------------

# Each case is (name, sig, expected). sig is a fully normalized signal table
# row (as produced by SignalTable.add()). expected is the list of dicts that
# _flatten_signal() must produce.

SINGLE_ENDED_CASES = [
    (
        "scalar",
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
        [
            {"pin": "G22", "iostandard": "LVCMOS18", "direction": "in", "buffer": "ibuf", "infer": False, "instance": "ibuf_sys_clk_i0", "is_bus": False, "index": 0},
        ],
    ),
    (
        "bus",
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
        [
            {"pin": "A22", "iostandard": "LVCMOS18", "direction": "out", "buffer": "obuf", "infer": False, "instance": "obuf_led_i0", "is_bus": True, "index": 0},
            {"pin": "B22", "iostandard": "LVCMOS18", "direction": "out", "buffer": "obuf", "infer": False, "instance": "obuf_led_i1", "is_bus": True, "index": 1},
            {"pin": "C22", "iostandard": "LVCMOS18", "direction": "out", "buffer": "obuf", "infer": False, "instance": "obuf_led_i2", "is_bus": True, "index": 2},
            {"pin": "D22", "iostandard": "LVCMOS18", "direction": "out", "buffer": "obuf", "infer": False, "instance": "obuf_led_i3", "is_bus": True, "index": 3},
        ],
    ),
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in SINGLE_ENDED_CASES],
)
def test_single_ended_row_shape(sig: dict, expected: list) -> None:
    """Single-ended signals produce the correct row list with all fields resolved."""
    assert _flatten_signal(sig) == expected


# ---------------------------------------------------------------------------
# Full row shape - differential
# ---------------------------------------------------------------------------

DIFFERENTIAL_CASES = [
    (
        "scalar",
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
        [
            {"pinset": {"p": "H22", "n": "H23"}, "iostandard": "LVDS", "direction": "in", "buffer": "ibufds", "infer": False, "instance": "ibufds_ref_clk_i0", "is_bus": False, "index": 0},
        ],
    ),
    (
        "bus",
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
        [
            {"pinset": {"p": "AA1", "n": "AA2"}, "iostandard": "LVDS", "direction": "out", "buffer": "obufds", "infer": False, "instance": "obufds_lvds_data_i0", "is_bus": True, "index": 0},
            {"pinset": {"p": "AB1", "n": "AB2"}, "iostandard": "LVDS", "direction": "out", "buffer": "obufds", "infer": False, "instance": "obufds_lvds_data_i1", "is_bus": True, "index": 1},
            {"pinset": {"p": "AC1", "n": "AC2"}, "iostandard": "LVDS", "direction": "out", "buffer": "obufds", "infer": False, "instance": "obufds_lvds_data_i2", "is_bus": True, "index": 2},
        ],
    ),
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in DIFFERENTIAL_CASES],
)
def test_differential_row_shape(sig: dict, expected: list) -> None:
    """Differential signals produce the correct row list with p/n pairs split per row."""
    assert _flatten_signal(sig) == expected


# ---------------------------------------------------------------------------
# bypass: true
# ---------------------------------------------------------------------------


def test_bypass_buffer_is_none() -> None:
    """bypass:true signals have buffer == None in every row."""
    sig = {
        "name": "spare",
        "pins": "J24",
        "width": 1,
        "direction": "out",
        "buffer": None,
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": False,
        "bypass": True,
        "comment": {},
        "instance": None,
    }
    rows = _flatten_signal(sig)
    assert all(r["buffer"] is None for r in rows)


def test_bypass_instance_is_none() -> None:
    """bypass:true signals have instance == None in every row."""
    sig = {
        "name": "spare",
        "pins": "J24",
        "width": 1,
        "direction": "out",
        "buffer": None,
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": False,
        "bypass": True,
        "comment": {},
        "instance": None,
    }
    rows = _flatten_signal(sig)
    assert all(r["instance"] is None for r in rows)


# ---------------------------------------------------------------------------
# infer: true
# ---------------------------------------------------------------------------


def test_infer_buffer_is_preserved() -> None:
    """infer:true signals retain the buffer type in every row."""
    sig = {
        "name": "sys_clk",
        "pins": "G22",
        "width": 1,
        "direction": "in",
        "buffer": "ibuf",
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": True,
        "bypass": False,
        "comment": {},
        "instance": "ibuf_sys_clk",
    }
    rows = _flatten_signal(sig)
    assert all(r["buffer"] == "ibuf" for r in rows)


def test_infer_instance_is_none() -> None:
    """infer:true signals have instance == None in every row."""
    sig = {
        "name": "sys_clk",
        "pins": "G22",
        "width": 1,
        "direction": "in",
        "buffer": "ibuf",
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": True,
        "bypass": False,
        "comment": {},
        "instance": "ibuf_sys_clk",
    }
    rows = _flatten_signal(sig)
    assert all(r["instance"] is None for r in rows)


# ---------------------------------------------------------------------------
# Instance name override
# ---------------------------------------------------------------------------


def test_instance_override_gets_suffix() -> None:
    """User-supplied instance base name gets _i<N> suffix appended."""
    sig = {
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
        "instance": "my_ibuf",
    }
    rows = _flatten_signal(sig)
    assert rows[0]["instance"] == "my_ibuf_i0"


def test_instance_override_bus_gets_suffix() -> None:
    """User-supplied instance base name gets _i<N> suffix for each bus element."""
    sig = {
        "name": "led",
        "pins": ["A22", "B22", "C22"],
        "width": 3,
        "direction": "out",
        "buffer": "obuf",
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": False,
        "bypass": False,
        "comment": {},
        "instance": "my_obuf",
    }
    rows = _flatten_signal(sig)
    assert [r["instance"] for r in rows] == ["my_obuf_i0", "my_obuf_i1", "my_obuf_i2"]


# ---------------------------------------------------------------------------
# is_bus derivation
# ---------------------------------------------------------------------------


def test_scalar_pins_is_bus_false() -> None:
    """Scalar pins string produces is_bus == False."""
    sig = {
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
    }
    rows = _flatten_signal(sig)
    assert rows[0]["is_bus"] is False


def test_array_pins_is_bus_true() -> None:
    """Array pins produces is_bus == True for every row."""
    sig = {
        "name": "led",
        "pins": ["A22", "B22"],
        "width": 2,
        "direction": "out",
        "buffer": "obuf",
        "iostandard": "LVCMOS18",
        "generate": True,
        "infer": False,
        "bypass": False,
        "comment": {},
        "instance": "obuf_led",
    }
    rows = _flatten_signal(sig)
    assert all(r["is_bus"] is True for r in rows)


def test_scalar_pinset_is_bus_false() -> None:
    """Scalar pinset produces is_bus == False."""
    sig = {
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
    }
    rows = _flatten_signal(sig)
    assert rows[0]["is_bus"] is False


def test_array_pinset_is_bus_true() -> None:
    """Array pinset produces is_bus == True for every row."""
    sig = {
        "name": "lvds_data",
        "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]},
        "width": 2,
        "direction": "out",
        "buffer": "obufds",
        "iostandard": "LVDS",
        "generate": True,
        "infer": False,
        "bypass": False,
        "comment": {},
        "instance": "obufds_lvds_data",
    }
    rows = _flatten_signal(sig)
    assert all(r["is_bus"] is True for r in rows)


# ---------------------------------------------------------------------------
# generate: false guard
# ---------------------------------------------------------------------------


def test_flatten_generate_false_raises() -> None:
    """Calling _flatten_signal on a generate:false row is a pipeline bug and must raise."""
    sig = {
        "name": "reserved_nc",
        "pins": "H24",
        "width": 1,
        "generate": False,
    }
    with pytest.raises(AssertionError):
        _flatten_signal(sig)
