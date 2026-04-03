import pytest

from io_gen.tables import SignalTable
from io_gen.tables.signal_table import build_signal_table

from io_gen.generate.common import _build_ioring_port_list


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


# ---- bypass conditions ------------------------------------------------------


def test_bypass_excluded() -> None:
    """bypass: true signals produce no entries in the IO ring port list."""
    st = _make_signal_table(
        [
            {
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
        ]
    )
    assert _build_ioring_port_list(st) == []


# ---- per-signal parametrized cases ------------------------------------------


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
        "scalar_inout",
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
        "bus_inout",
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
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in PORT_LIST_CASES],
)
def test_port_list_for_signal(sig: dict, expected: list[dict]) -> None:
    """Each signal type produces the correct port dicts in signal table order."""
    st = _make_signal_table([sig])
    assert _build_ioring_port_list(st) == expected


# ---- integration ------------------------------------------------------------


_INTEGRATION_SIGNALS = [
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
        "name": "lvds_data",
        "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
        "width": 3,
        "direction": "out",
        "buffer": "obufds",
        "iostandard": "LVDS",
    },
    {
        "name": "gpio",
        "pins": ["E22", "F22", "G23", "A23", "B23"],
        "width": 5,
        "direction": "inout",
        "buffer": "iobuf",
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

_EXPECTED_PORT_LIST = [
    {"name": "sys_clk_pad", "direction": "in", "width": 1, "is_bus": False},
    {"name": "sys_clk", "direction": "out", "width": 1, "is_bus": False},
    {"name": "led_pad", "direction": "out", "width": 4, "is_bus": True},
    {"name": "led", "direction": "in", "width": 4, "is_bus": True},
    {"name": "ref_clk_p", "direction": "in", "width": 1, "is_bus": False},
    {"name": "ref_clk_n", "direction": "in", "width": 1, "is_bus": False},
    {"name": "ref_clk", "direction": "out", "width": 1, "is_bus": False},
    {"name": "lvds_data_p", "direction": "out", "width": 3, "is_bus": True},
    {"name": "lvds_data_n", "direction": "out", "width": 3, "is_bus": True},
    {"name": "lvds_data", "direction": "in", "width": 3, "is_bus": True},
    {"name": "gpio_pad", "direction": "inout", "width": 5, "is_bus": True},
    {"name": "gpio_i", "direction": "out", "width": 5, "is_bus": True},
    {"name": "gpio_o", "direction": "in", "width": 5, "is_bus": True},
    {"name": "gpio_t", "direction": "in", "width": 5, "is_bus": True},
]


def test_integration_port_list() -> None:
    """Full signal set produces the expected flat port list in signal table order."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _build_ioring_port_list(st) == _EXPECTED_PORT_LIST
