import pytest

from io_gen.tables import SignalTable, PinTable
from io_gen.tables.signal_table import build_signal_table
from io_gen.tables.pin_table import build_pin_table

from io_gen.generate.verilog_ioring import (
    _infer_ibuf,
    _infer_obuf,
    _instantiate_ibuf,
    _instantiate_obuf,
    _instantiate_ibufds,
    _instantiate_obufds,
    _instantiate_iobuf,
    _generate_verilog_ioring_ports,
    _generate_verilog_ioring_body,
    generate_verilog_ioring,
)


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


def _make_tables(signals: list) -> tuple[SignalTable, PinTable]:
    st = _make_signal_table(signals)
    pt = build_pin_table(st)
    return st, pt


# ---- helpers ---------------------------------------------------------------


def _scalar_ibuf_row(name: str, instance: str) -> dict:
    return {
        "pin": "G22",
        "iostandard": "LVCMOS18",
        "direction": "in",
        "buffer": "ibuf",
        "infer": False,
        "instance": instance,
        "is_bus": False,
        "index": 0,
    }


def _bus_ibuf_row(name: str, instance: str, index: int) -> dict:
    return {
        "pin": "G22",
        "iostandard": "LVCMOS18",
        "direction": "in",
        "buffer": "ibuf",
        "infer": False,
        "instance": instance,
        "is_bus": True,
        "index": index,
    }


def _scalar_obuf_row(name: str, instance: str) -> dict:
    return {
        "pin": "A22",
        "iostandard": "LVCMOS18",
        "direction": "out",
        "buffer": "obuf",
        "infer": False,
        "instance": instance,
        "is_bus": False,
        "index": 0,
    }


def _bus_obuf_row(name: str, instance: str, index: int) -> dict:
    return {
        "pin": "A22",
        "iostandard": "LVCMOS18",
        "direction": "out",
        "buffer": "obuf",
        "infer": False,
        "instance": instance,
        "is_bus": True,
        "index": index,
    }


# ---- _infer_ibuf -----------------------------------------------------------


def test_infer_ibuf_returns_str() -> None:
    assert isinstance(_infer_ibuf("sys_clk"), str)


def test_infer_ibuf_assignment() -> None:
    """Input inference: fabric signal assigned from pad port."""
    assert _infer_ibuf("sys_clk") == "    assign sys_clk = sys_clk_pad;"


def test_infer_ibuf_bus() -> None:
    """Bus inference collapses to a single assignment, not per-bit."""
    assert _infer_ibuf("data") == "    assign data = data_pad;"


# ---- _infer_obuf -----------------------------------------------------------


def test_infer_obuf_returns_str() -> None:
    assert isinstance(_infer_obuf("led"), str)


def test_infer_obuf_assignment() -> None:
    """Output inference: pad port assigned from fabric signal."""
    assert _infer_obuf("led") == "    assign led_pad = led;"


def test_infer_obuf_bus() -> None:
    """Bus inference collapses to a single assignment, not per-bit."""
    assert _infer_obuf("data") == "    assign data_pad = data;"


# ---- _instantiate_ibuf -----------------------------------------------------


def test_instantiate_ibuf_returns_str() -> None:
    row = _scalar_ibuf_row("sys_clk", "ibuf_sys_clk_i0")
    assert isinstance(_instantiate_ibuf("sys_clk", row), str)


def test_instantiate_ibuf_scalar() -> None:
    """Scalar IBUF instantiation using Xilinx port order: O then I."""
    row = _scalar_ibuf_row("sys_clk", "ibuf_sys_clk_i0")
    expected = (
        "    IBUF //#(\n"
        "    //)\n"
        "    ibuf_sys_clk_i0 (\n"
        "        .O  (sys_clk),\n"
        "        .I  (sys_clk_pad)\n"
        "    );"
    )
    assert _instantiate_ibuf("sys_clk", row) == expected


def test_instantiate_ibuf_bus_first_element() -> None:
    """Bus IBUF at index 0 uses subscript notation on both ports."""
    row = _bus_ibuf_row("data", "ibuf_data_i0", 0)
    expected = (
        "    IBUF //#(\n"
        "    //)\n"
        "    ibuf_data_i0 (\n"
        "        .O  (data[0]),\n"
        "        .I  (data_pad[0])\n"
        "    );"
    )
    assert _instantiate_ibuf("data", row) == expected


def test_instantiate_ibuf_bus_mid_element() -> None:
    """Bus IBUF at index 2 uses the correct subscript on both ports."""
    row = _bus_ibuf_row("data", "ibuf_data_i2", 2)
    expected = (
        "    IBUF //#(\n"
        "    //)\n"
        "    ibuf_data_i2 (\n"
        "        .O  (data[2]),\n"
        "        .I  (data_pad[2])\n"
        "    );"
    )
    assert _instantiate_ibuf("data", row) == expected


# ---- _instantiate_obuf -----------------------------------------------------


def test_instantiate_obuf_returns_str() -> None:
    row = _scalar_obuf_row("led", "obuf_led_i0")
    assert isinstance(_instantiate_obuf("led", row), str)


def test_instantiate_obuf_scalar() -> None:
    """Scalar OBUF instantiation using Xilinx port order: O then I."""
    row = _scalar_obuf_row("led", "obuf_led_i0")
    expected = (
        "    OBUF //#(\n"
        "    //)\n"
        "    obuf_led_i0 (\n"
        "        .O  (led_pad),\n"
        "        .I  (led)\n"
        "    );"
    )
    assert _instantiate_obuf("led", row) == expected


def test_instantiate_obuf_bus_first_element() -> None:
    """Bus OBUF at index 0 uses subscript notation on both ports."""
    row = _bus_obuf_row("led", "obuf_led_i0", 0)
    expected = (
        "    OBUF //#(\n"
        "    //)\n"
        "    obuf_led_i0 (\n"
        "        .O  (led_pad[0]),\n"
        "        .I  (led[0])\n"
        "    );"
    )
    assert _instantiate_obuf("led", row) == expected


def test_instantiate_obuf_bus_last_element() -> None:
    """Bus OBUF at index 3 uses the correct subscript on both ports."""
    row = _bus_obuf_row("led", "obuf_led_i3", 3)
    expected = (
        "    OBUF //#(\n"
        "    //)\n"
        "    obuf_led_i3 (\n"
        "        .O  (led_pad[3]),\n"
        "        .I  (led[3])\n"
        "    );"
    )
    assert _instantiate_obuf("led", row) == expected


# ---- _instantiate_ibufds ---------------------------------------------------


def _scalar_ibufds_row(instance: str) -> dict:
    return {
        "pinset": {"p": "H22", "n": "H23"},
        "iostandard": "LVDS",
        "direction": "in",
        "buffer": "ibufds",
        "infer": False,
        "instance": instance,
        "is_bus": False,
        "index": 0,
    }


def _bus_ibufds_row(instance: str, index: int) -> dict:
    return {
        "pinset": {"p": "H22", "n": "H23"},
        "iostandard": "LVDS",
        "direction": "in",
        "buffer": "ibufds",
        "infer": False,
        "instance": instance,
        "is_bus": True,
        "index": index,
    }


def test_instantiate_ibufds_returns_str() -> None:
    row = _scalar_ibufds_row("ibufds_ref_clk_i0")
    assert isinstance(_instantiate_ibufds("ref_clk", row), str)


def test_instantiate_ibufds_scalar() -> None:
    """Scalar IBUFDS using Xilinx port order: O, I, IB."""
    row = _scalar_ibufds_row("ibufds_ref_clk_i0")
    expected = (
        "    IBUFDS //#(\n"
        "    //)\n"
        "    ibufds_ref_clk_i0 (\n"
        "        .O  (ref_clk),\n"
        "        .I  (ref_clk_p),\n"
        "        .IB (ref_clk_n)\n"
        "    );"
    )
    assert _instantiate_ibufds("ref_clk", row) == expected


def test_instantiate_ibufds_bus() -> None:
    """Bus IBUFDS uses subscript on all three ports."""
    row = _bus_ibufds_row("ibufds_ref_clk_i1", 1)
    expected = (
        "    IBUFDS //#(\n"
        "    //)\n"
        "    ibufds_ref_clk_i1 (\n"
        "        .O  (ref_clk[1]),\n"
        "        .I  (ref_clk_p[1]),\n"
        "        .IB (ref_clk_n[1])\n"
        "    );"
    )
    assert _instantiate_ibufds("ref_clk", row) == expected


# ---- _instantiate_obufds ---------------------------------------------------


def _scalar_obufds_row(instance: str) -> dict:
    return {
        "pinset": {"p": "AA1", "n": "AA2"},
        "iostandard": "LVDS",
        "direction": "out",
        "buffer": "obufds",
        "infer": False,
        "instance": instance,
        "is_bus": False,
        "index": 0,
    }


def _bus_obufds_row(instance: str, index: int) -> dict:
    return {
        "pinset": {"p": "AA1", "n": "AA2"},
        "iostandard": "LVDS",
        "direction": "out",
        "buffer": "obufds",
        "infer": False,
        "instance": instance,
        "is_bus": True,
        "index": index,
    }


def test_instantiate_obufds_returns_str() -> None:
    row = _scalar_obufds_row("obufds_lvds_data_i0")
    assert isinstance(_instantiate_obufds("lvds_data", row), str)


def test_instantiate_obufds_scalar() -> None:
    """Scalar OBUFDS using Xilinx port order: O, OB, I."""
    row = _scalar_obufds_row("obufds_lvds_data_i0")
    expected = (
        "    OBUFDS //#(\n"
        "    //)\n"
        "    obufds_lvds_data_i0 (\n"
        "        .O  (lvds_data_p),\n"
        "        .OB (lvds_data_n),\n"
        "        .I  (lvds_data)\n"
        "    );"
    )
    assert _instantiate_obufds("lvds_data", row) == expected


def test_instantiate_obufds_bus() -> None:
    """Bus OBUFDS uses subscript on all three ports."""
    row = _bus_obufds_row("obufds_lvds_data_i2", 2)
    expected = (
        "    OBUFDS //#(\n"
        "    //)\n"
        "    obufds_lvds_data_i2 (\n"
        "        .O  (lvds_data_p[2]),\n"
        "        .OB (lvds_data_n[2]),\n"
        "        .I  (lvds_data[2])\n"
        "    );"
    )
    assert _instantiate_obufds("lvds_data", row) == expected


# ---- _instantiate_iobuf ----------------------------------------------------


def _scalar_iobuf_row(instance: str) -> dict:
    return {
        "pin": "E22",
        "iostandard": "LVCMOS18",
        "direction": "inout",
        "buffer": "iobuf",
        "infer": False,
        "instance": instance,
        "is_bus": False,
        "index": 0,
    }


def _bus_iobuf_row(instance: str, index: int) -> dict:
    return {
        "pin": "E22",
        "iostandard": "LVCMOS18",
        "direction": "inout",
        "buffer": "iobuf",
        "infer": False,
        "instance": instance,
        "is_bus": True,
        "index": index,
    }


def test_instantiate_iobuf_returns_str() -> None:
    row = _scalar_iobuf_row("iobuf_gpio_i0")
    assert isinstance(_instantiate_iobuf("gpio", row), str)


def test_instantiate_iobuf_scalar() -> None:
    """Scalar IOBUF using Xilinx port order: O, I, IO, T."""
    row = _scalar_iobuf_row("iobuf_gpio_i0")
    expected = (
        "    IOBUF //#(\n"
        "    //)\n"
        "    iobuf_gpio_i0 (\n"
        "        .O  (gpio_i),\n"
        "        .I  (gpio_o),\n"
        "        .IO (gpio_pad),\n"
        "        .T  (gpio_t)\n"
        "    );"
    )
    assert _instantiate_iobuf("gpio", row) == expected


def test_instantiate_iobuf_bus() -> None:
    """Bus IOBUF uses subscript on all four ports."""
    row = _bus_iobuf_row("iobuf_gpio_i3", 3)
    expected = (
        "    IOBUF //#(\n"
        "    //)\n"
        "    iobuf_gpio_i3 (\n"
        "        .O  (gpio_i[3]),\n"
        "        .I  (gpio_o[3]),\n"
        "        .IO (gpio_pad[3]),\n"
        "        .T  (gpio_t[3])\n"
        "    );"
    )
    assert _instantiate_iobuf("gpio", row) == expected


# ---- _generate_verilog_ioring_ports ----------------------------------------

# Reuse the integration signal set from test_verilog_top
_IORING_INTEGRATION_SIGNALS = [
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

PORT_DECL_CASES = [
    (
        "scalar_se_input_pad_port",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "input   wire            sys_clk_pad",
    ),
    (
        "scalar_se_input_fabric_port",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "output  wire            sys_clk",
    ),
    (
        "bus_se_output_pad_port",
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "output  wire [3:0]      led_pad",
    ),
    (
        "bus_se_output_fabric_port",
        {
            "name": "led",
            "pins": ["A22", "B22", "C22", "D22"],
            "width": 4,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "input   wire [3:0]      led",
    ),
    (
        "scalar_se_inout_pad_port",
        {
            "name": "gpio",
            "pins": "A22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        "inout   wire            gpio_pad",
    ),
    (
        "scalar_se_inout_fabric_i",
        {
            "name": "gpio",
            "pins": "A22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        "output  wire            gpio_i",
    ),
    (
        "scalar_se_inout_fabric_o",
        {
            "name": "gpio",
            "pins": "A22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        "input   wire            gpio_o",
    ),
    (
        "scalar_se_inout_fabric_t",
        {
            "name": "gpio",
            "pins": "A22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        "input   wire            gpio_t",
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
        "input   wire            ref_clk_p",
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
        "input   wire            ref_clk_n",
    ),
    (
        "scalar_diff_input_fabric",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        "output  wire            ref_clk",
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
        "output  wire [2:0]      lvds_data_p",
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
        "output  wire [2:0]      lvds_data_n",
    ),
    (
        "bus_diff_output_fabric",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]},
            "width": 3,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "input   wire [2:0]      lvds_data",
    ),
    (
        "bus_width_16_pad_port",
        {
            "name": "data",
            "pins": [f"A{i}" for i in range(16)],
            "width": 16,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "output  wire [15:0]     data_pad",
    ),
    (
        "bus_width_16_fabric_port",
        {
            "name": "data",
            "pins": [f"A{i}" for i in range(16)],
            "width": 16,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "input   wire [15:0]     data",
    ),
]


def test_generate_verilog_ioring_ports_returns_str() -> None:
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
    assert isinstance(_generate_verilog_ioring_ports(st), str)


@pytest.mark.parametrize(
    "sig, expected_decl",
    [pytest.param(s, d, id=n) for n, s, d in PORT_DECL_CASES],
)
def test_ioring_port_decl_in_output(sig: dict, expected_decl: str) -> None:
    """The correct port declaration appears in the output for each signal type."""
    st = _make_signal_table([sig])
    assert expected_decl in _generate_verilog_ioring_ports(st)


def test_ioring_ports_all_bypass() -> None:
    """A signal table where every signal is bypass:true produces an empty string."""
    st = _make_signal_table(
        [
            {
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
            {
                "name": "spare2",
                "pins": "K24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
        ]
    )
    assert _generate_verilog_ioring_ports(st) == ""


def test_ioring_ports_bypass_excluded() -> None:
    """bypass:true signals produce no port declarations in the IO ring."""
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
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
        ]
    )
    assert "spare" not in _generate_verilog_ioring_ports(st)


def test_ioring_ports_no_trailing_comma_on_last_port() -> None:
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
    output = _generate_verilog_ioring_ports(st)
    last_line = [ln for ln in output.splitlines() if ln.strip()][-1]
    assert not last_line.endswith(",")


def test_ioring_ports_no_trailing_comma_when_last_signal_is_bypass() -> None:
    """The last non-bypass port has no trailing comma when the last table entry is bypass:true."""
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
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
        ]
    )
    output = _generate_verilog_ioring_ports(st)
    last_line = [ln for ln in output.splitlines() if ln.strip()][-1]
    assert not last_line.endswith(",")


_EXPECTED_IORING_PORTS = (
    "    input   wire            sys_clk_pad,\n"
    "    output  wire            sys_clk,\n"
    "    output  wire [3:0]      led_pad,\n"
    "    input   wire [3:0]      led,\n"
    "    input   wire            ref_clk_p,\n"
    "    input   wire            ref_clk_n,\n"
    "    output  wire            ref_clk,\n"
    "    output  wire [2:0]      lvds_data_p,\n"
    "    output  wire [2:0]      lvds_data_n,\n"
    "    input   wire [2:0]      lvds_data,\n"
    "    inout   wire [4:0]      gpio_pad,\n"
    "    output  wire [4:0]      gpio_i,\n"
    "    input   wire [4:0]      gpio_o,\n"
    "    input   wire [4:0]      gpio_t"
)


def test_ioring_ports_integration() -> None:
    """Full signal set produces the expected IO ring port list. spare is bypass:true and excluded."""
    st = _make_signal_table(_IORING_INTEGRATION_SIGNALS)
    assert _generate_verilog_ioring_ports(st) == _EXPECTED_IORING_PORTS


# ---- _generate_verilog_ioring_body -----------------------------------------


def test_ioring_body_returns_str() -> None:
    st, pt = _make_tables(
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
    assert isinstance(_generate_verilog_ioring_body(st, pt), str)


def test_ioring_body_scalar_ibuf() -> None:
    """Scalar IBUF produces a single instantiation block."""
    st, pt = _make_tables(
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
    expected = (
        "    IBUF //#(\n"
        "    //)\n"
        "    ibuf_sys_clk_i0 (\n"
        "        .O  (sys_clk),\n"
        "        .I  (sys_clk_pad)\n"
        "    );"
    )
    assert _generate_verilog_ioring_body(st, pt) == expected


def test_ioring_body_bus_obuf() -> None:
    """Bus OBUF produces one instantiation per bit, separated by blank lines."""
    st, pt = _make_tables(
        [
            {
                "name": "led",
                "pins": ["A22", "B22"],
                "width": 2,
                "direction": "out",
                "buffer": "obuf",
                "iostandard": "LVCMOS18",
            }
        ]
    )
    output = _generate_verilog_ioring_body(st, pt)
    assert "obuf_led_i0" in output
    assert "obuf_led_i1" in output
    assert "led_pad[0]" in output
    assert "led_pad[1]" in output
    # blank line between instances
    assert "\n\n" in output


def test_ioring_body_bypass_excluded() -> None:
    """bypass:true signals produce no output in the body."""
    st, pt = _make_tables(
        [
            {
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            }
        ]
    )
    assert _generate_verilog_ioring_body(st, pt) == ""


def test_ioring_body_infer_ibuf() -> None:
    """infer:true IBUF produces an assign statement, not an instantiation."""
    st, pt = _make_tables(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
                "infer": True,
            }
        ]
    )
    output = _generate_verilog_ioring_body(st, pt)
    assert "assign sys_clk = sys_clk_pad;" in output
    assert "IBUF" not in output


def test_ioring_body_infer_obuf() -> None:
    """infer:true OBUF produces an assign statement, not an instantiation."""
    st, pt = _make_tables(
        [
            {
                "name": "led",
                "pins": "A22",
                "direction": "out",
                "buffer": "obuf",
                "iostandard": "LVCMOS18",
                "infer": True,
            }
        ]
    )
    output = _generate_verilog_ioring_body(st, pt)
    assert "assign led_pad = led;" in output
    assert "OBUF" not in output


def test_ioring_body_mixed_bypass_and_normal() -> None:
    """bypass:true signals are excluded while normal signals still appear."""
    st, pt = _make_tables(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
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
    )
    output = _generate_verilog_ioring_body(st, pt)
    assert "ibuf_sys_clk_i0" in output
    assert "spare" not in output


def test_ioring_body_all_bypass() -> None:
    """A signal table where every signal is bypass:true produces an empty string."""
    st, pt = _make_tables(
        [
            {
                "name": "spare",
                "pins": "J24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
            {
                "name": "spare2",
                "pins": "K24",
                "direction": "out",
                "iostandard": "LVCMOS18",
                "bypass": True,
            },
        ]
    )
    assert _generate_verilog_ioring_body(st, pt) == ""


def test_ioring_body_ibufds_scalar() -> None:
    """Scalar IBUFDS produces a single instantiation block."""
    st, pt = _make_tables(
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
    output = _generate_verilog_ioring_body(st, pt)
    assert "IBUFDS" in output
    assert "ibufds_ref_clk_i0" in output
    assert "ref_clk_p" in output
    assert "ref_clk_n" in output
    assert "ref_clk)" in output


def test_ioring_body_obufds_bus() -> None:
    """Bus OBUFDS produces one instantiation per pair, separated by blank lines."""
    st, pt = _make_tables(
        [
            {
                "name": "lvds_data",
                "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]},
                "width": 2,
                "direction": "out",
                "buffer": "obufds",
                "iostandard": "LVDS",
            }
        ]
    )
    output = _generate_verilog_ioring_body(st, pt)
    assert "obufds_lvds_data_i0" in output
    assert "obufds_lvds_data_i1" in output
    assert "\n\n" in output


def test_ioring_body_iobuf_bus() -> None:
    """Bus IOBUF produces one instantiation per bit with _i, _o, _t fabric ports."""
    st, pt = _make_tables(
        [
            {
                "name": "gpio",
                "pins": ["E22", "F22", "G23"],
                "width": 3,
                "direction": "inout",
                "buffer": "iobuf",
                "iostandard": "LVCMOS18",
            }
        ]
    )
    output = _generate_verilog_ioring_body(st, pt)
    assert "iobuf_gpio_i0" in output
    assert "iobuf_gpio_i2" in output
    assert "gpio_i[0]" in output
    assert "gpio_o[0]" in output
    assert "gpio_t[0]" in output
    assert "gpio_pad[0]" in output
    assert "\n\n" in output


# ---- generate_verilog_ioring -----------------------------------------------


def test_generate_verilog_ioring_returns_str() -> None:
    st, pt = _make_tables(
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
    assert isinstance(generate_verilog_ioring(st, pt, "test"), str)


def test_generate_verilog_ioring_file_header() -> None:
    """Output begins with commented blank, do-not-edit lines, commented blank."""
    st, pt = _make_tables(
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
    output = generate_verilog_ioring(st, pt, "test")
    lines = output.splitlines()
    assert lines[0] == "//"
    assert lines[1] == "// Generated by io-gen - do not edit"
    assert lines[2] == "// Regenerate from source YAML using io-gen"
    assert lines[3] == "//"


def test_generate_verilog_ioring_header() -> None:
    """Module name is <top>_io with commented parameter block on separate lines."""
    st, pt = _make_tables(
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
    output = generate_verilog_ioring(st, pt, "test")
    lines = output.splitlines()
    assert lines[4] == "module test_io //#("
    assert lines[5] == "//)"
    assert lines[6] == "("


def test_generate_verilog_ioring_endmodule() -> None:
    """endmodule is the last line of the output."""
    st, pt = _make_tables(
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
    output = generate_verilog_ioring(st, pt, "test")
    assert output.splitlines()[-1] == "endmodule"


def test_generate_verilog_ioring_ports_present() -> None:
    """Port declarations appear between the opening '(' and ');'."""
    st, pt = _make_tables(
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
    output = generate_verilog_ioring(st, pt, "test")
    assert "sys_clk_pad" in output
    assert "sys_clk" in output


def test_generate_verilog_ioring_body_present() -> None:
    """Buffer instantiation appears in the module body."""
    st, pt = _make_tables(
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
    output = generate_verilog_ioring(st, pt, "test")
    assert "ibuf_sys_clk_i0" in output


def test_generate_verilog_ioring_ends_with_newline() -> None:
    """Output ends with a trailing newline."""
    st, pt = _make_tables(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
                "infer": False,
            },
        ]
    )
    assert generate_verilog_ioring(st, pt, "test").endswith("\n")


def test_generate_verilog_ioring_integration() -> None:
    """Full signal set matches example_io.v structure. spare is bypass:true and excluded."""
    st, pt = _make_tables(_IORING_INTEGRATION_SIGNALS)
    output = generate_verilog_ioring(st, pt, "example")
    lines = output.splitlines()
    assert lines[0] == "//"
    assert lines[1] == "// Generated by io-gen - do not edit"
    assert lines[4] == "module example_io //#("
    assert lines[-1] == "endmodule"
    assert "spare" not in output
    # All buffer types present
    assert "IBUF" in output
    assert "OBUF" in output
    assert "IBUFDS" in output
    assert "OBUFDS" in output
    assert "IOBUF" in output
    # All instance names present
    assert "ibuf_sys_clk_i0" in output
    assert "obuf_led_i3" in output
    assert "ibufds_ref_clk_i0" in output
    assert "obufds_lvds_data_i2" in output
    assert "iobuf_gpio_i4" in output
