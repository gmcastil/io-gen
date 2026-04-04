import pytest

from io_gen.generate.verilog_ioring import (
    _infer_ibuf,
    _infer_obuf,
    _instantiate_ibuf,
    _instantiate_obuf,
    _instantiate_ibufds,
    _instantiate_obufds,
    _instantiate_iobuf,
)


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
