import pytest

from io_gen.tables import SignalTable

from io_gen.generate.verilog_top import _generate_verilog_ports, _generate_verilog_wires
from io_gen.tables.signal_table import build_signal_table


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


# ---- _generate_verilog_ports ------------------------------------------------


def test_generate_verilog_ports_returns_str() -> None:
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
    assert isinstance(_generate_verilog_ports(st), str)


PORT_DECL_CASES = [
    (
        "scalar_se_input",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "input  wire        sys_clk_pad",
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
        "output wire [3:0]  led_pad",
    ),
    (
        "scalar_diff_input_p",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        "input  wire        ref_clk_p",
    ),
    (
        "scalar_diff_input_n",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        "input  wire        ref_clk_n",
    ),
    (
        "bus_diff_output_p",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
            "width": 3,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "output wire [2:0]  lvds_data_p",
    ),
    (
        "bus_diff_output_n",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
            "width": 3,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "output wire [2:0]  lvds_data_n",
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
        "inout  wire [4:0]  gpio_pad",
    ),
    (
        "scalar_se_bypass",
        {
            "name": "spare",
            "pins": "J24",
            "direction": "out",
            "iostandard": "LVCMOS18",
            "bypass": True,
        },
        "output wire        spare_pad",
    ),
]


@pytest.mark.parametrize(
    "sig, expected_decl",
    [pytest.param(s, d, id=n) for n, s, d in PORT_DECL_CASES],
)
def test_port_decl_in_output(sig: dict, expected_decl: str) -> None:
    """The correct port declaration appears in the output for each signal type."""
    st = _make_signal_table([sig])
    assert expected_decl in _generate_verilog_ports(st)


def test_hdl_comment_emitted() -> None:
    """comment.hdl is emitted as a // line before the port declaration."""
    st = _make_signal_table(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
                "comment": {"hdl": "125 MHz system clock input"},
            },
        ]
    )
    assert "// 125 MHz system clock input" in _generate_verilog_ports(st)


def test_no_hdl_comment_no_slash_line() -> None:
    """A signal with no comment.hdl produces no // line."""
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
    assert "//" not in _generate_verilog_ports(st)



def test_no_trailing_comma_on_last_port() -> None:
    """The last port declaration has no trailing comma."""
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
                "pins": ["A22", "B22"],
                "width": 2,
                "direction": "out",
                "buffer": "obuf",
                "iostandard": "LVCMOS18",
            },
        ]
    )
    output = _generate_verilog_ports(st)
    last_line = [ln for ln in output.splitlines() if ln.strip()][-1]
    assert not last_line.endswith(",")


# ---- integration -----------------------------------------------------------

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
]

_EXPECTED_PORTS = (
    "    // 125 MHz system clock input\n"
    "    input  wire        sys_clk_pad,\n"
    "    // User LED outputs\n"
    "    output wire [3:0]  led_pad,\n"
    "    // 200 MHz differential reference clock input\n"
    "    input  wire        ref_clk_p,\n"
    "    input  wire        ref_clk_n,\n"
    "    // LVDS serial data outputs\n"
    "    output wire [2:0]  lvds_data_p,\n"
    "    output wire [2:0]  lvds_data_n,\n"
    "    // General purpose IO\n"
    "    inout  wire [4:0]  gpio_pad,\n"
    "    // Spare output, driven directly\n"
    "    output wire        spare_pad"
)


def test_integration_output() -> None:
    """Full signal set produces the expected port list string."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _generate_verilog_ports(st) == _EXPECTED_PORTS


# ---- _generate_verilog_wires -----------------------------------------------


WIRE_DECL_CASES = [
    (
        "scalar_se_input",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        ["    wire            sys_clk;"],
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
        ["    wire    [3:0]   led;"],
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
        ["    wire            ref_clk;"],
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
        ["    wire    [2:0]   lvds_data;"],
    ),
    (
        "scalar_iobuf",
        {
            "name": "gpio",
            "pins": "A22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        ["    wire            gpio_i;", "    wire            gpio_o;", "    wire            gpio_t;"],
    ),
    (
        "bus_iobuf",
        {
            "name": "gpio",
            "pins": ["A22", "B22", "C22"],
            "width": 3,
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        ["    wire    [2:0]   gpio_i;", "    wire    [2:0]   gpio_o;", "    wire    [2:0]   gpio_t;"],
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
        ["    wire    [0:0]   led;"],
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
        ["    wire    [0:0]   gpio_i;", "    wire    [0:0]   gpio_o;", "    wire    [0:0]   gpio_t;"],
    ),
]


@pytest.mark.parametrize(
    "sig, expected_lines",
    [pytest.param(s, e, id=n) for n, s, e in WIRE_DECL_CASES],
)
def test_wire_decl_in_output(sig: dict, expected_lines: list[str]) -> None:
    """The correct wire declaration(s) appear in the output for each signal type."""
    st = _make_signal_table([sig])
    output = _generate_verilog_wires(st)
    for line in expected_lines:
        assert line in output


def test_bypass_excluded_from_wires() -> None:
    """bypass:true signals produce no wire declaration."""
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
    assert "spare" not in _generate_verilog_wires(st)



_EXPECTED_WIRES = (
    "    wire            sys_clk;\n"
    "    wire    [3:0]   led;\n"
    "    wire            ref_clk;\n"
    "    wire    [2:0]   lvds_data;\n"
    "    wire    [4:0]   gpio_i;\n"
    "    wire    [4:0]   gpio_o;\n"
    "    wire    [4:0]   gpio_t;"
)


def test_wires_integration_output() -> None:
    """Full signal set produces the expected wire block string."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _generate_verilog_wires(st) == _EXPECTED_WIRES
