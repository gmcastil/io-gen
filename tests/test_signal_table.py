import pytest

from io_gen.tables.signal_table import SignalTable, build_signal_table


# ---------------------------------------------------------------------------
# SignalTable container behavior
# ---------------------------------------------------------------------------


def test_empty_table() -> None:
    """An empty SignalTable has length zero and yields nothing on iteration."""
    table = SignalTable()
    assert len(table) == 0
    assert list(table) == []


def test_add_single() -> None:
    """Adding one signal produces length 1."""
    table = SignalTable()
    table.add({"name": "sys_clk", "pins": "G22", "direction": "in", "buffer": "ibuf", "iostandard": "LVCMOS18"})
    assert len(table) == 1


def test_add_multiple_preserves_order() -> None:
    """Rows are returned in insertion order."""
    table = SignalTable()
    table.add({"name": "a", "pins": "G22", "direction": "in", "buffer": "ibuf", "iostandard": "LVCMOS18"})
    table.add({"name": "b", "pins": "H22", "direction": "out", "buffer": "obuf", "iostandard": "LVCMOS18"})
    table.add({"name": "c", "pins": "H24", "generate": False})
    assert len(table) == 3
    assert [row["name"] for row in table] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# add() - row shapes (generate: true)
# ---------------------------------------------------------------------------

# Each case is (name, sig, expected_row). sig is the raw signal dict as it
# would come from the YAML. expected_row is the fully resolved dict that
# add() must produce, including all normalized defaults.

GENERATE_TRUE_SHAPE_CASES = [
    (
        "scalar_single_ended",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        {
            "name": "sys_clk",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "width": 1,
            "pins": "G22",
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibuf_sys_clk",
        },
    ),
    (
        "bus_single_ended",
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        {
            "name": "led",
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "width": 4,
            "pins": ["A22", "B22", "C22", "D22"],
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obuf_led",
        },
    ),
    (
        "scalar_differential",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        {
            "name": "ref_clk",
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
            "width": 1,
            "pinset": {"p": "H22", "n": "H23"},
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "ibufds_ref_clk",
        },
    ),
    (
        "bus_differential",
        {
            "name": "lvds_data",
            "pinset": {
                "p": ["AA1", "AB1", "AC1"],
                "n": ["AA2", "AB2", "AC2"],
            },
            "width": 3,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        {
            "name": "lvds_data",
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
            "width": 3,
            "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "obufds_lvds_data",
        },
    ),
    (
        "scalar_inout_single_ended",
        {
            "name": "gpio",
            "pins": "E22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        {
            "name": "gpio",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
            "width": 1,
            "pins": "E22",
            "generate": True,
            "infer": False,
            "bypass": False,
            "comment": {},
            "instance": "iobuf_gpio",
        },
    ),
    (
        "bypass_single_ended",
        {
            "name": "spare",
            "pins": "J24",
            "direction": "out",
            "iostandard": "LVCMOS18",
            "bypass": True,
        },
        {
            "name": "spare",
            "direction": "out",
            "buffer": None,
            "iostandard": "LVCMOS18",
            "width": 1,
            "pins": "J24",
            "generate": True,
            "infer": False,
            "bypass": True,
            "comment": {},
            "instance": None,
        },
    ),
]


@pytest.mark.parametrize(
    "sig, expected_row",
    [pytest.param(s, r, id=n) for n, s, r in GENERATE_TRUE_SHAPE_CASES],
)
def test_generate_true_row_shape(sig: dict, expected_row: dict) -> None:
    """Each generate:true signal produces a fully resolved row with all expected fields."""
    table = SignalTable()
    table.add(sig)
    rows = list(table)
    assert len(rows) == 1
    assert rows[0] == expected_row


# ---------------------------------------------------------------------------
# add() - row shapes (generate: false)
# ---------------------------------------------------------------------------

GENERATE_FALSE_SHAPE_CASES = [
    (
        "single_ended_scalar",
        {
            "name": "reserved_nc",
            "pins": "H24",
            "generate": False,
        },
        {
            "name": "reserved_nc",
            "pins": "H24",
            "width": 1,
            "generate": False,
        },
    ),
    (
        "single_ended_bus",
        {
            "name": "reserved_bus",
            "pins": ["A1", "A2", "A3"],
            "width": 3,
            "generate": False,
        },
        {
            "name": "reserved_bus",
            "pins": ["A1", "A2", "A3"],
            "width": 3,
            "generate": False,
        },
    ),
    (
        "differential_scalar",
        {
            "name": "reserved_diff",
            "pinset": {"p": "H22", "n": "H23"},
            "generate": False,
        },
        {
            "name": "reserved_diff",
            "pinset": {"p": "H22", "n": "H23"},
            "width": 1,
            "generate": False,
        },
    ),
    (
        "differential_bus",
        {
            "name": "reserved_diff_bus",
            "pinset": {
                "p": ["AA1", "AB1"],
                "n": ["AA2", "AB2"],
            },
            "width": 2,
            "generate": False,
        },
        {
            "name": "reserved_diff_bus",
            "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]},
            "width": 2,
            "generate": False,
        },
    ),
]


@pytest.mark.parametrize(
    "sig, expected_row",
    [pytest.param(s, r, id=n) for n, s, r in GENERATE_FALSE_SHAPE_CASES],
)
def test_generate_false_row_shape(sig: dict, expected_row: dict) -> None:
    """generate:false signals produce a reduced row with exactly the required keys."""
    table = SignalTable()
    table.add(sig)
    rows = list(table)
    assert len(rows) == 1
    assert rows[0] == expected_row


GENERATE_FALSE_ABSENT_KEYS = [
    "direction",
    "buffer",
    "iostandard",
    "infer",
    "bypass",
    "comment",
    "instance",
]


@pytest.mark.parametrize(
    "key",
    [pytest.param(k, id=k) for k in GENERATE_FALSE_ABSENT_KEYS],
)
def test_generate_false_absent_keys(key: str) -> None:
    """generate:false rows must not contain generate:true-only keys."""
    table = SignalTable()
    table.add({"name": "reserved_nc", "pins": "H24", "generate": False})
    row = list(table)[0]
    assert key not in row


# ---------------------------------------------------------------------------
# add() - normalization defaults
# ---------------------------------------------------------------------------

# Each case: (name, sig, field, expected_value). sig omits the field being
# tested; add() must supply the default.

NORMALIZATION_DEFAULTS = [
    (
        "generate_defaults_true",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "generate",
        True,
    ),
    (
        "infer_defaults_false",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "infer",
        False,
    ),
    (
        "bypass_defaults_false",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "bypass",
        False,
    ),
    (
        "comment_defaults_empty_dict",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "comment",
        {},
    ),
    (
        "width_defaults_one_for_scalar",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "width",
        1,
    ),
    (
        "instance_autogenerated",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "instance",
        "ibuf_sys_clk",
    ),
]


@pytest.mark.parametrize(
    "sig, field, expected",
    [pytest.param(s, f, e, id=n) for n, s, f, e in NORMALIZATION_DEFAULTS],
)
def test_normalization_defaults(sig: dict, field: str, expected: object) -> None:
    """Fields absent from the YAML are normalized to their default values."""
    table = SignalTable()
    table.add(sig)
    row = list(table)[0]
    assert row[field] == expected


# ---------------------------------------------------------------------------
# add() - special cases
# ---------------------------------------------------------------------------


def test_bypass_signal() -> None:
    """bypass:true signals have buffer == None and instance == None."""
    table = SignalTable()
    table.add({
        "name": "spare",
        "pins": "J24",
        "direction": "out",
        "iostandard": "LVCMOS18",
        "bypass": True,
    })
    row = list(table)[0]
    assert row["buffer"] is None
    assert row["instance"] is None
    assert row["bypass"] is True


def test_infer_true() -> None:
    """infer:true is preserved in the row."""
    table = SignalTable()
    table.add({
        "name": "sys_clk",
        "pins": "G22",
        "direction": "in",
        "buffer": "ibuf",
        "iostandard": "LVCMOS18",
        "infer": True,
    })
    row = list(table)[0]
    assert row["infer"] is True


def test_comment_preserved() -> None:
    """Comment dict is copied into the row unchanged."""
    table = SignalTable()
    table.add({
        "name": "sys_clk",
        "pins": "G22",
        "direction": "in",
        "buffer": "ibuf",
        "iostandard": "LVCMOS18",
        "comment": {"xdc": "125 MHz clock", "hdl": "system clock"},
    })
    row = list(table)[0]
    assert row["comment"] == {"xdc": "125 MHz clock", "hdl": "system clock"}


def test_instance_override() -> None:
    """User-supplied instance is stored as the base name without _iN suffix."""
    table = SignalTable()
    table.add({
        "name": "sys_clk",
        "pins": "G22",
        "direction": "in",
        "buffer": "ibuf",
        "iostandard": "LVCMOS18",
        "instance": "my_ibuf",
    })
    row = list(table)[0]
    assert row["instance"] == "my_ibuf"


# ---------------------------------------------------------------------------
# build_signal_table() - integration
# ---------------------------------------------------------------------------


def test_build_signal_table_count_and_order() -> None:
    """build_signal_table produces one row per signal in YAML order."""
    doc = {
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
                "pins": ["A22", "B22"],
                "width": 2,
                "direction": "out",
                "buffer": "obuf",
                "iostandard": "LVCMOS18",
            },
            {
                "name": "reserved_nc",
                "pins": "H24",
                "generate": False,
            },
        ],
    }
    table = build_signal_table(doc)
    rows = list(table)
    assert len(rows) == 3
    assert rows[0]["name"] == "sys_clk"
    assert rows[1]["name"] == "led"
    assert rows[2]["name"] == "reserved_nc"
