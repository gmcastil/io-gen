import pytest

from io_gen.tables import SignalTable
from io_gen.tables.signal_table import build_signal_table

from io_gen.generate.common import _build_ioring_port_list


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


# ---- _build_ioring_port_list -------------------------------------------------


def test_build_ioring_port_list_returns_list() -> None:
    st = _make_signal_table(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
            },
        ]
    )
    result = _build_ioring_port_list(st)
    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert isinstance(result[0][0], dict)


IORING_PORT_LIST_CASES = [
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
            {"direction": "in",  "name": "sys_clk_pad", "width": 1, "is_bus": False},
            {"direction": "out", "name": "sys_clk",     "width": 1, "is_bus": False},
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
            {"direction": "out", "name": "led_pad", "width": 4, "is_bus": True},
            {"direction": "in",  "name": "led",     "width": 4, "is_bus": True},
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
            {"direction": "in",  "name": "ref_clk_p", "width": 1, "is_bus": False},
            {"direction": "in",  "name": "ref_clk_n", "width": 1, "is_bus": False},
            {"direction": "out", "name": "ref_clk",   "width": 1, "is_bus": False},
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
            {"direction": "out", "name": "lvds_data_p", "width": 3, "is_bus": True},
            {"direction": "out", "name": "lvds_data_n", "width": 3, "is_bus": True},
            {"direction": "in",  "name": "lvds_data",   "width": 3, "is_bus": True},
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
            {"direction": "inout", "name": "gpio_pad", "width": 5, "is_bus": True},
            {"direction": "out",   "name": "gpio_i",   "width": 5, "is_bus": True},
            {"direction": "in",    "name": "gpio_o",   "width": 5, "is_bus": True},
            {"direction": "in",    "name": "gpio_t",   "width": 5, "is_bus": True},
        ],
    ),
    (
        "scalar_se_infer",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "infer": True,
        },
        [
            {"direction": "in",  "name": "sys_clk_pad", "width": 1, "is_bus": False},
            {"direction": "out", "name": "sys_clk",     "width": 1, "is_bus": False},
        ],
    ),
]


@pytest.mark.parametrize(
    "sig, expected_group",
    [pytest.param(s, e, id=n) for n, s, e in IORING_PORT_LIST_CASES],
)
def test_ioring_port_list_group(sig: dict, expected_group: list[dict]) -> None:
    """Each signal produces the correct port group (pad-facing then fabric-facing)."""
    st = _make_signal_table([sig])
    result = _build_ioring_port_list(st)
    assert len(result) == 1
    assert result[0] == expected_group


def test_bypass_excluded() -> None:
    """bypass:true signals are excluded from the IO ring port list."""
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


def test_generate_false_excluded() -> None:
    """generate:false signals are excluded from the IO ring port list."""
    st = _make_signal_table(
        [
            {"name": "reserved_nc", "pins": "H24", "generate": False},
        ]
    )
    assert _build_ioring_port_list(st) == []


def test_one_group_per_signal() -> None:
    """Each signal produces exactly one inner list regardless of pin count."""
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
                "name": "led",
                "pins": ["A22", "B22", "C22", "D22"],
                "width": 4,
                "direction": "out",
                "buffer": "obuf",
                "iostandard": "LVCMOS18",
            },
        ]
    )
    result = _build_ioring_port_list(st)
    assert len(result) == 2


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
    {"name": "reserved_nc", "pins": "H24", "generate": False},
]

_EXPECTED_PORT_LIST = [
    [
        {"direction": "in",  "name": "sys_clk_pad", "width": 1, "is_bus": False},
        {"direction": "out", "name": "sys_clk",     "width": 1, "is_bus": False},
    ],
    [
        {"direction": "out", "name": "led_pad", "width": 4, "is_bus": True},
        {"direction": "in",  "name": "led",     "width": 4, "is_bus": True},
    ],
    [
        {"direction": "in",  "name": "ref_clk_p", "width": 1, "is_bus": False},
        {"direction": "in",  "name": "ref_clk_n", "width": 1, "is_bus": False},
        {"direction": "out", "name": "ref_clk",   "width": 1, "is_bus": False},
    ],
    [
        {"direction": "out", "name": "lvds_data_p", "width": 3, "is_bus": True},
        {"direction": "out", "name": "lvds_data_n", "width": 3, "is_bus": True},
        {"direction": "in",  "name": "lvds_data",   "width": 3, "is_bus": True},
    ],
    [
        {"direction": "inout", "name": "gpio_pad", "width": 5, "is_bus": True},
        {"direction": "out",   "name": "gpio_i",   "width": 5, "is_bus": True},
        {"direction": "in",    "name": "gpio_o",   "width": 5, "is_bus": True},
        {"direction": "in",    "name": "gpio_t",   "width": 5, "is_bus": True},
    ],
]


def test_integration_port_list() -> None:
    """Full signal set produces the expected list[list[dict]] structure."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _build_ioring_port_list(st) == _EXPECTED_PORT_LIST
