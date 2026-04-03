import pytest

from io_gen.tables import SignalTable
from io_gen.tables.signal_table import build_signal_table
from io_gen.generate.verilog_ioring import _build_ioring_port_list


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


# ---- _build_ioring_port_list ------------------------------------------------
#
# Returns list[tuple[str, str, int]]: (port_name, direction, width)
# Direction is from the ioring module's perspective:
#   - Pad-facing ports: same direction as the signal
#   - Fabric input signals (direction=in): fabric port is "out" (ioring drives fabric)
#   - Fabric output signals (direction=out): fabric port is "in" (ioring receives)
#   - Tristate fabric ports: _i="out", _o="in", _t="in"
# Bypass signals are excluded entirely. generate:false signals are excluded.

PORT_LIST_CASES = [
    (
        "scalar_se_input",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        [("sys_clk_pad", "in", 1), ("sys_clk", "out", 1)],
    ),
    (
        "bus_se_output",
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        [("led_pad", "out", 4), ("led", "in", 4)],
    ),
    (
        "scalar_diff_input",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        [("ref_clk_p", "in", 1), ("ref_clk_n", "in", 1), ("ref_clk", "out", 1)],
    ),
    (
        "bus_diff_input",
        {
            "name": "clk_bank",
            "pinset": {"p": ["H22", "J22"], "n": ["H23", "J23"]},
            "width": 2,
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        [("clk_bank_p", "in", 2), ("clk_bank_n", "in", 2), ("clk_bank", "out", 2)],
    ),
    (
        "bus_diff_output",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
            "width": 3,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        [("lvds_data_p", "out", 3), ("lvds_data_n", "out", 3), ("lvds_data", "in", 3)],
    ),
    (
        "scalar_se_inout",
        {
            "name": "gpio",
            "pins": "A22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        [
            ("gpio_pad", "inout", 1),
            ("gpio_i", "out", 1),
            ("gpio_o", "in", 1),
            ("gpio_t", "in", 1),
        ],
    ),
    (
        "bus_se_inout",
        {
            "name": "gpio",
            "pins": ["E22", "F22", "G23", "A23", "B23"],
            "width": 5,
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        [
            ("gpio_pad", "inout", 5),
            ("gpio_i", "out", 5),
            ("gpio_o", "in", 5),
            ("gpio_t", "in", 5),
        ],
    ),
    (
        "bus_length_1_se",
        {
            "name": "led",
            "pins": ["A22"],
            "width": 1,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        [("led_pad", "out", 1), ("led", "in", 1)],
    ),
    (
        "bus_length_1_iobuf",
        {
            "name": "gpio",
            "pins": ["A22"],
            "width": 1,
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        [
            ("gpio_pad", "inout", 1),
            ("gpio_i", "out", 1),
            ("gpio_o", "in", 1),
            ("gpio_t", "in", 1),
        ],
    ),
    (
        "scalar_se_infer",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "infer": True,
            "iostandard": "LVCMOS18",
        },
        [("sys_clk_pad", "in", 1), ("sys_clk", "out", 1)],
    ),
    (
        "bypass_excluded",
        {
            "name": "spare",
            "pins": "J24",
            "direction": "out",
            "iostandard": "LVCMOS18",
            "bypass": True,
        },
        [],
    ),
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in PORT_LIST_CASES],
)
def test_port_list_entries(sig: dict, expected: list[tuple[str, str, int]]) -> None:
    """Each signal type produces the correct port list entries."""
    st = _make_signal_table([sig])
    assert _build_ioring_port_list(st) == expected


def test_generate_false_excluded() -> None:
    """generate:false signals produce no entries in the port list."""
    st = _make_signal_table([{"name": "reserved_nc", "pins": "H24", "generate": False}])
    assert _build_ioring_port_list(st) == []


def test_pad_before_fabric_se() -> None:
    """Pad-facing port appears before fabric-facing port for SE signals."""
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
    names = [name for name, _, _ in _build_ioring_port_list(st)]
    assert names.index("sys_clk_pad") < names.index("sys_clk")


def test_pad_before_fabric_diff() -> None:
    """Both pad-facing ports appear before the fabric-facing port for differential signals."""
    st = _make_signal_table(
        [
            {
                "name": "ref_clk",
                "pinset": {"p": "H22", "n": "H23"},
                "direction": "in",
                "buffer": "ibufds",
                "iostandard": "LVDS",
            }
        ]
    )
    names = [name for name, _, _ in _build_ioring_port_list(st)]
    assert names.index("ref_clk_p") < names.index("ref_clk")
    assert names.index("ref_clk_n") < names.index("ref_clk")


def test_pad_before_fabric_iobuf() -> None:
    """Pad-facing port appears before all three fabric-facing ports for tristate signals."""
    st = _make_signal_table(
        [
            {
                "name": "gpio",
                "pins": "A22",
                "direction": "inout",
                "buffer": "iobuf",
                "iostandard": "LVCMOS18",
            }
        ]
    )
    names = [name for name, _, _ in _build_ioring_port_list(st)]
    pad_idx = names.index("gpio_pad")
    assert pad_idx < names.index("gpio_i")
    assert pad_idx < names.index("gpio_o")
    assert pad_idx < names.index("gpio_t")


# ---- integration ------------------------------------------------------------

_INTEGRATION_SIGNALS = [
    {
        "name": "sys_clk",
        "pins": "G22",
        "direction": "in",
        "buffer": "ibuf",
        "iostandard": "LVCMOS18",
        "comment": {"hdl": "125 MHz system clock input"},
    },
    {
        "name": "led",
        "pins": ["A22", "B22", "C22", "D22"],
        "width": 4,
        "direction": "out",
        "buffer": "obuf",
        "iostandard": "LVCMOS18",
        "comment": {"hdl": "User LED outputs"},
    },
    {
        "name": "ref_clk",
        "pinset": {"p": "H22", "n": "H23"},
        "direction": "in",
        "buffer": "ibufds",
        "iostandard": "LVDS",
        "comment": {"hdl": "200 MHz differential reference clock input"},
    },
    {
        "name": "lvds_data",
        "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
        "width": 3,
        "direction": "out",
        "buffer": "obufds",
        "iostandard": "LVDS",
        "comment": {"hdl": "LVDS serial data outputs"},
    },
    {
        "name": "gpio",
        "pins": ["E22", "F22", "G23", "A23", "B23"],
        "width": 5,
        "direction": "inout",
        "buffer": "iobuf",
        "iostandard": "LVCMOS18",
        "comment": {"hdl": "General purpose IO"},
    },
    {
        "name": "spare",
        "pins": "J24",
        "direction": "out",
        "iostandard": "LVCMOS18",
        "bypass": True,
        "comment": {"hdl": "Spare output, driven directly"},
    },
    {"name": "reserved_nc", "pins": "H24", "generate": False},
]

_EXPECTED_PORT_LIST = [
    ("sys_clk_pad", "in", 1),
    ("sys_clk", "out", 1),
    ("led_pad", "out", 4),
    ("led", "in", 4),
    ("ref_clk_p", "in", 1),
    ("ref_clk_n", "in", 1),
    ("ref_clk", "out", 1),
    ("lvds_data_p", "out", 3),
    ("lvds_data_n", "out", 3),
    ("lvds_data", "in", 3),
    ("gpio_pad", "inout", 5),
    ("gpio_i", "out", 5),
    ("gpio_o", "in", 5),
    ("gpio_t", "in", 5),
]


def test_integration_port_list() -> None:
    """Full signal set produces the complete expected port list, bypass and generate:false excluded."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _build_ioring_port_list(st) == _EXPECTED_PORT_LIST
