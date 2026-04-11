import pytest

from io_gen.tables import SignalTable
from io_gen.tables.signal_table import build_signal_table

from io_gen.generate.common import get_signal_top_ports, get_signal_ioring_ports


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


def _make_sig_row(sig: dict) -> dict:
    """Build a normalized signal table row from a raw signal dict."""
    return list(_make_signal_table([sig]))[0]


# ---- _get_signal_top_ports --------------------------------------------------

TOP_PORT_CASES = [
    (
        "scalar_se_input",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        [{"name": "sys_clk_pad", "direction": "in", "width": 1, "is_bus": False}],
    ),
    (
        "scalar_se_output",
        {
            "name": "led",
            "pins": "A22",
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        [{"name": "led_pad", "direction": "out", "width": 1, "is_bus": False}],
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
        [{"name": "gpio_pad", "direction": "inout", "width": 1, "is_bus": False}],
    ),
    (
        "bus_se_input",
        {
            "name": "data",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        [{"name": "data_pad", "direction": "in", "width": 4, "is_bus": True}],
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
        [{"name": "led_pad", "direction": "out", "width": 4, "is_bus": True}],
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
        [{"name": "gpio_pad", "direction": "inout", "width": 5, "is_bus": True}],
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
        [
            {"name": "ref_clk_p", "direction": "in", "width": 1, "is_bus": False},
            {"name": "ref_clk_n", "direction": "in", "width": 1, "is_bus": False},
        ],
    ),
    (
        "scalar_diff_output",
        {
            "name": "lvds_out",
            "pinset": {"p": "AA1", "n": "AA2"},
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        [
            {"name": "lvds_out_p", "direction": "out", "width": 1, "is_bus": False},
            {"name": "lvds_out_n", "direction": "out", "width": 1, "is_bus": False},
        ],
    ),
    (
        "bus_diff_input",
        {
            "name": "ref_clk",
            "pinset": {"p": ["H22", "H24"], "n": ["H23", "H25"]},
            "width": 2,
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        [
            {"name": "ref_clk_p", "direction": "in", "width": 2, "is_bus": True},
            {"name": "ref_clk_n", "direction": "in", "width": 2, "is_bus": True},
        ],
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
        [
            {"name": "lvds_data_p", "direction": "out", "width": 3, "is_bus": True},
            {"name": "lvds_data_n", "direction": "out", "width": 3, "is_bus": True},
        ],
    ),
    (
        "bypass_included",
        {
            "name": "spare",
            "pins": "J24",
            "direction": "out",
            "iostandard": "LVCMOS18",
            "bypass": True,
        },
        [{"name": "spare_pad", "direction": "out", "width": 1, "is_bus": False}],
    ),
    (
        "infer_included",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "infer": True,
        },
        [{"name": "sys_clk_pad", "direction": "in", "width": 1, "is_bus": False}],
    ),
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in TOP_PORT_CASES],
)
def test_get_signal_top_ports(sig: dict, expected: list[dict]) -> None:
    """Each signal type produces the correct top-level port entries."""
    row = _make_sig_row(sig)
    assert get_signal_top_ports(row) == expected


# ---- _get_signal_ioring_ports -----------------------------------------------

IORING_PORT_CASES = [
    (
        "scalar_se_input",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        [
            {"name": "sys_clk_pad", "direction": "in", "width": 1, "is_bus": False},
            {"name": "sys_clk", "direction": "out", "width": 1, "is_bus": False},
        ],
    ),
    (
        "scalar_se_output",
        {
            "name": "led",
            "pins": "A22",
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        [
            {"name": "led_pad", "direction": "out", "width": 1, "is_bus": False},
            {"name": "led", "direction": "in", "width": 1, "is_bus": False},
        ],
    ),
    (
        "bus_se_input",
        {
            "name": "data",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        [
            {"name": "data_pad", "direction": "in", "width": 4, "is_bus": True},
            {"name": "data", "direction": "out", "width": 4, "is_bus": True},
        ],
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
        [
            {"name": "led_pad", "direction": "out", "width": 4, "is_bus": True},
            {"name": "led", "direction": "in", "width": 4, "is_bus": True},
        ],
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
            {"name": "gpio_pad", "direction": "inout", "width": 1, "is_bus": False},
            {"name": "gpio_i", "direction": "out", "width": 1, "is_bus": False},
            {"name": "gpio_o", "direction": "in", "width": 1, "is_bus": False},
            {"name": "gpio_t", "direction": "in", "width": 1, "is_bus": False},
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
            {"name": "gpio_pad", "direction": "inout", "width": 5, "is_bus": True},
            {"name": "gpio_i", "direction": "out", "width": 5, "is_bus": True},
            {"name": "gpio_o", "direction": "in", "width": 5, "is_bus": True},
            {"name": "gpio_t", "direction": "in", "width": 5, "is_bus": True},
        ],
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
        [
            {"name": "ref_clk_p", "direction": "in", "width": 1, "is_bus": False},
            {"name": "ref_clk_n", "direction": "in", "width": 1, "is_bus": False},
            {"name": "ref_clk", "direction": "out", "width": 1, "is_bus": False},
        ],
    ),
    (
        "scalar_diff_output",
        {
            "name": "lvds_out",
            "pinset": {"p": "AA1", "n": "AA2"},
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        [
            {"name": "lvds_out_p", "direction": "out", "width": 1, "is_bus": False},
            {"name": "lvds_out_n", "direction": "out", "width": 1, "is_bus": False},
            {"name": "lvds_out", "direction": "in", "width": 1, "is_bus": False},
        ],
    ),
    (
        "bus_diff_input",
        {
            "name": "ref_clk",
            "pinset": {"p": ["H22", "H24"], "n": ["H23", "H25"]},
            "width": 2,
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        [
            {"name": "ref_clk_p", "direction": "in", "width": 2, "is_bus": True},
            {"name": "ref_clk_n", "direction": "in", "width": 2, "is_bus": True},
            {"name": "ref_clk", "direction": "out", "width": 2, "is_bus": True},
        ],
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
        [
            {"name": "lvds_data_p", "direction": "out", "width": 3, "is_bus": True},
            {"name": "lvds_data_n", "direction": "out", "width": 3, "is_bus": True},
            {"name": "lvds_data", "direction": "in", "width": 3, "is_bus": True},
        ],
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
    (
        "infer_same_ports_as_normal",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "infer": True,
        },
        [
            {"name": "sys_clk_pad", "direction": "in", "width": 1, "is_bus": False},
            {"name": "sys_clk", "direction": "out", "width": 1, "is_bus": False},
        ],
    ),
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in IORING_PORT_CASES],
)
def test_get_signal_ioring_ports(sig: dict, expected: list[dict]) -> None:
    """Each signal type produces the correct IO ring port entries."""
    row = _make_sig_row(sig)
    assert get_signal_ioring_ports(row) == expected
