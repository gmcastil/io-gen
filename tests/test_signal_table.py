import pytest

from io_gen.tables.signal_table import SignalTable, build_signal_table


# ---------------------------------------------------------------------------
# SignalTable class
# ---------------------------------------------------------------------------


def test_empty_table() -> None:
    """An empty SignalTable has length zero and yields nothing on iteration."""
    table = SignalTable()
    assert len(table) == 0
    assert list(table) == []


def test_add_single() -> None:
    """Adding one row produces length 1 and iteration yields that row."""
    table = SignalTable()
    row = {"name": "sys_clk", "generate": True}
    table.add(row)
    assert len(table) == 1
    assert list(table) == [row]


def test_add_multiple_preserves_order() -> None:
    """Rows are returned in insertion order."""
    table = SignalTable()
    rows = [
        {"name": "a", "generate": True},
        {"name": "b", "generate": True},
        {"name": "c", "generate": True},
    ]
    for row in rows:
        table.add(row)
    assert len(table) == 3
    assert list(table) == rows


# ---------------------------------------------------------------------------
# build_signal_table - row shapes (generate: true)
# ---------------------------------------------------------------------------

# Each case is (name, doc, expected_row). The doc contains a single signal.
# The expected_row is the fully resolved dict the table should produce,
# including all normalized defaults.

GENERATE_TRUE_SHAPE_CASES = [
    (
        "scalar_single_ended",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "direction": "in",
                    "buffer": "ibuf",
                    "iostandard": "LVCMOS18",
                }
            ],
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
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "led",
                    "pins": ["A22", "B22", "C22", "D22"],
                    "width": 4,
                    "direction": "out",
                    "buffer": "obuf",
                    "iostandard": "LVCMOS18",
                }
            ],
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
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "ref_clk",
                    "pinset": {"p": "H22", "n": "H23"},
                    "direction": "in",
                    "buffer": "ibufds",
                    "iostandard": "LVDS",
                }
            ],
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
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
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
                }
            ],
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
]


@pytest.mark.parametrize(
    "doc, expected_row",
    [pytest.param(d, r, id=n) for n, d, r in GENERATE_TRUE_SHAPE_CASES],
)
def test_generate_true_row_shape(doc: dict, expected_row: dict) -> None:
    """Each generate:true signal produces a fully resolved row with all expected fields."""
    table = build_signal_table(doc)
    rows = list(table)
    assert len(rows) == 1
    assert rows[0] == expected_row


# ---------------------------------------------------------------------------
# build_signal_table - row shapes (generate: false)
# ---------------------------------------------------------------------------

GENERATE_FALSE_SHAPE_CASES = [
    (
        "single_ended",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "reserved_nc",
                    "pins": "H24",
                    "generate": False,
                }
            ],
        },
        {
            "name": "reserved_nc",
            "pins": "H24",
            "width": 1,
            "generate": False,
        },
    ),
    (
        "differential",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "reserved_diff",
                    "pinset": {"p": "H22", "n": "H23"},
                    "generate": False,
                }
            ],
        },
        {
            "name": "reserved_diff",
            "pinset": {"p": "H22", "n": "H23"},
            "width": 1,
            "generate": False,
        },
    ),
]


@pytest.mark.parametrize(
    "doc, expected_row",
    [pytest.param(d, r, id=n) for n, d, r in GENERATE_FALSE_SHAPE_CASES],
)
def test_generate_false_row_shape(doc: dict, expected_row: dict) -> None:
    """generate:false signals produce a reduced row with exactly the required keys."""
    table = build_signal_table(doc)
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
    doc = {
        "title": "Test",
        "part": "xc7k325tffg900-2",
        "signals": [{"name": "reserved_nc", "pins": "H24", "generate": False}],
    }
    table = build_signal_table(doc)
    row = list(table)[0]
    assert key not in row


# ---------------------------------------------------------------------------
# build_signal_table - normalization defaults
# ---------------------------------------------------------------------------

# Each case: (name, doc, field, expected_value). The doc omits the field
# being tested; the factory must supply the default.

NORMALIZATION_DEFAULTS = [
    (
        "infer_defaults_false",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "direction": "in",
                    "buffer": "ibuf",
                    "iostandard": "LVCMOS18",
                }
            ],
        },
        "infer",
        False,
    ),
    (
        "bypass_defaults_false",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "direction": "in",
                    "buffer": "ibuf",
                    "iostandard": "LVCMOS18",
                }
            ],
        },
        "bypass",
        False,
    ),
    (
        "comment_defaults_empty_dict",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "direction": "in",
                    "buffer": "ibuf",
                    "iostandard": "LVCMOS18",
                }
            ],
        },
        "comment",
        {},
    ),
    (
        "width_defaults_one_for_scalar",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "direction": "in",
                    "buffer": "ibuf",
                    "iostandard": "LVCMOS18",
                }
            ],
        },
        "width",
        1,
    ),
    (
        "instance_autogenerated",
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "direction": "in",
                    "buffer": "ibuf",
                    "iostandard": "LVCMOS18",
                }
            ],
        },
        "instance",
        "ibuf_sys_clk",
    ),
]


@pytest.mark.parametrize(
    "doc, field, expected",
    [pytest.param(d, f, e, id=n) for n, d, f, e in NORMALIZATION_DEFAULTS],
)
def test_normalization_defaults(doc: dict, field: str, expected: object) -> None:
    """Fields absent from the YAML are normalized to their default values."""
    table = build_signal_table(doc)
    row = list(table)[0]
    assert row[field] == expected


# ---------------------------------------------------------------------------
# build_signal_table - special cases
# ---------------------------------------------------------------------------


def test_bypass_signal() -> None:
    """bypass:true signals have buffer == None and instance == None."""
    doc = {
        "title": "Test",
        "part": "xc7k325tffg900-2",
        "signals": [
            {
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            }
        ],
    }
    table = build_signal_table(doc)
    row = list(table)[0]
    assert row["buffer"] is None
    assert row["instance"] is None
    assert row["bypass"] is True


def test_infer_true() -> None:
    """infer:true is preserved in the row."""
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
                "infer": True,
            }
        ],
    }
    table = build_signal_table(doc)
    row = list(table)[0]
    assert row["infer"] is True


def test_comment_preserved() -> None:
    """Comment dict is copied into the row unchanged."""
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
                "comment": {"xdc": "125 MHz clock", "hdl": "system clock"},
            }
        ],
    }
    table = build_signal_table(doc)
    row = list(table)[0]
    assert row["comment"] == {"xdc": "125 MHz clock", "hdl": "system clock"}


def test_instance_override() -> None:
    """User-supplied instance is stored as the base name without _iN suffix."""
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
                "instance": "my_ibuf",
            }
        ],
    }
    table = build_signal_table(doc)
    row = list(table)[0]
    assert row["instance"] == "my_ibuf"


def test_multiple_signals_preserves_order() -> None:
    """Multiple signals produce one row each in YAML order."""
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
