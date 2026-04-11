import pytest

from io_gen.tables import SignalTable
from io_gen.tables.signal_table import build_signal_table
from io_gen.tables.meta_table import MetaTable

from io_gen.generate.vhdl_top import (
    _generate_vhdl_ports,
    _generate_vhdl_signals,
    _generate_vhdl_ioring_inst,
    generate_vhdl_top,
)

_TEST_META = MetaTable(title="Test", part="xc7k325tffg900-2", architecture="rtl")


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return build_signal_table(doc)


# ---- _generate_vhdl_ports --------------------------------------------------


def test_generate_vhdl_ports_returns_str() -> None:
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
    assert isinstance(_generate_vhdl_ports(st), str)


# Each case builds a single-signal table and asserts the complete output string.
# name_len = ((len(longest_port_name) // 4) + 1) * 4; indent = level 2 (8 spaces).
# Differential signals produce two ports combined into one expected string.
# Last port has no trailing semicolon.

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
        # port: sys_clk_pad (11), name_len = 12
        "        sys_clk_pad : in    std_logic",
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
        # port: led_pad (7), name_len = 8
        "        led_pad : out   std_logic_vector(3 downto 0)",
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
        # ports: ref_clk_p, ref_clk_n (9), name_len = 12
        "        ref_clk_p   : in    std_logic;\n"
        "        ref_clk_n   : in    std_logic",
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
        # ports: lvds_data_p, lvds_data_n (11), name_len = 12
        "        lvds_data_p : out   std_logic_vector(2 downto 0);\n"
        "        lvds_data_n : out   std_logic_vector(2 downto 0)",
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
        # port: gpio_pad (8), name_len = 12
        "        gpio_pad    : inout std_logic_vector(4 downto 0)",
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
        # port: spare_pad (9), name_len = 12
        "        spare_pad   : out   std_logic",
    ),
    (
        "bus_width_16",
        {
            "name": "data",
            "pins": [f"A{i}" for i in range(16)],
            "width": 16,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        # port: data_pad (8), name_len = 12
        "        data_pad    : out   std_logic_vector(15 downto 0)",
    ),
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in PORT_DECL_CASES],
)
def test_port_decl_output(sig: dict, expected: str) -> None:
    """Complete port declaration output for each signal type."""
    st = _make_signal_table([sig])
    assert _generate_vhdl_ports(st) == expected


def test_hdl_comment_emitted() -> None:
    """comment.hdl is emitted as a -- line before the port declaration."""
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
    # port: sys_clk_pad (11), name_len = 12
    expected = (
        "        -- 125 MHz system clock input\n"
        "        sys_clk_pad : in    std_logic"
    )
    assert _generate_vhdl_ports(st) == expected


def test_no_hdl_comment_no_dash_line() -> None:
    """A signal with no comment.hdl produces no -- line."""
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
    assert "--" not in _generate_vhdl_ports(st)


def test_no_trailing_semicolon_on_last_port() -> None:
    """The last port declaration has no trailing semicolon."""
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
    # ports: sys_clk_pad (11), led_pad (7); name_len = 12
    expected = (
        "        sys_clk_pad : in    std_logic;\n"
        "        led_pad     : out   std_logic_vector(1 downto 0)"
    )
    assert _generate_vhdl_ports(st) == expected


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
        "name": "user_led",
        "pins": "K22",
        "direction": "out",
        "buffer": "obuf",
        "infer": True,
        "iostandard": "LVCMOS18",
        "comment": {"hdl": "User LED output, buffer inferred"},
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

# longest port name = user_led_pad (12), name_len = 16
_EXPECTED_PORTS = (
    "        -- 125 MHz system clock input\n"
    "        sys_clk_pad     : in    std_logic;\n"
    "        -- User LED outputs\n"
    "        led_pad         : out   std_logic_vector(3 downto 0);\n"
    "        -- User LED output, buffer inferred\n"
    "        user_led_pad    : out   std_logic;\n"
    "        -- 200 MHz differential reference clock input\n"
    "        ref_clk_p       : in    std_logic;\n"
    "        ref_clk_n       : in    std_logic;\n"
    "        -- LVDS serial data outputs\n"
    "        lvds_data_p     : out   std_logic_vector(2 downto 0);\n"
    "        lvds_data_n     : out   std_logic_vector(2 downto 0);\n"
    "        -- General purpose IO\n"
    "        gpio_pad        : inout std_logic_vector(4 downto 0);\n"
    "        -- Spare output, driven directly\n"
    "        spare_pad       : out   std_logic"
)


def test_ports_integration_output() -> None:
    """Full signal set produces the expected port list string."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _generate_vhdl_ports(st) == _EXPECTED_PORTS


# ---- _generate_vhdl_signals ------------------------------------------------

# Each case builds a single-signal table and asserts the complete output string.
# name_len = ((len("signal " + longest_net_name) // 4) + 1) * 4; indent = level 1 (4 spaces).
# iobuf expands to three declarations: <name>_i, <name>_o, <name>_t.

SIGNAL_DECL_CASES = [
    (
        "scalar_se_input",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        # lhs = "signal sys_clk" (14), name_len = 16
        "    signal sys_clk  : std_logic;",
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
        # lhs = "signal led" (10), name_len = 12
        "    signal led  : std_logic_vector(3 downto 0);",
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
        # lhs = "signal ref_clk" (14), name_len = 16
        "    signal ref_clk  : std_logic;",
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
        # lhs = "signal lvds_data" (16), name_len = 20
        "    signal lvds_data    : std_logic_vector(2 downto 0);",
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
        # lhs = "signal gpio_i/o/t" (13), name_len = 16
        "    signal gpio_i   : std_logic;\n"
        "    signal gpio_o   : std_logic;\n"
        "    signal gpio_t   : std_logic;",
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
        # lhs = "signal gpio_i/o/t" (13), name_len = 16
        "    signal gpio_i   : std_logic_vector(2 downto 0);\n"
        "    signal gpio_o   : std_logic_vector(2 downto 0);\n"
        "    signal gpio_t   : std_logic_vector(2 downto 0);",
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
        # lhs = "signal led" (10), name_len = 12
        "    signal led  : std_logic_vector(0 downto 0);",
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
        # lhs = "signal gpio_i/o/t" (13), name_len = 16
        "    signal gpio_i   : std_logic_vector(0 downto 0);\n"
        "    signal gpio_o   : std_logic_vector(0 downto 0);\n"
        "    signal gpio_t   : std_logic_vector(0 downto 0);",
    ),
    (
        "bus_width_16_se",
        {
            "name": "data",
            "pins": [f"A{i}" for i in range(16)],
            "width": 16,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        # lhs = "signal data" (11), name_len = 12
        "    signal data : std_logic_vector(15 downto 0);",
    ),
    (
        "bus_width_16_iobuf",
        {
            "name": "data",
            "pins": [f"A{i}" for i in range(16)],
            "width": 16,
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        # lhs = "signal data_i/o/t" (13), name_len = 16
        "    signal data_i   : std_logic_vector(15 downto 0);\n"
        "    signal data_o   : std_logic_vector(15 downto 0);\n"
        "    signal data_t   : std_logic_vector(15 downto 0);",
    ),
]


@pytest.mark.parametrize(
    "sig, expected",
    [pytest.param(s, e, id=n) for n, s, e in SIGNAL_DECL_CASES],
)
def test_signal_decl_output(sig: dict, expected: str) -> None:
    """Complete signal declaration output for each signal type."""
    st = _make_signal_table([sig])
    assert _generate_vhdl_signals(st) == expected


def test_bypass_excluded_from_signals() -> None:
    """bypass:true signals produce no signal declaration."""
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
    assert "spare" not in _generate_vhdl_signals(st)


def test_signals_all_bypass_returns_empty_string() -> None:
    """All-bypass signal table produces an empty string, not a ValueError."""
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
    assert _generate_vhdl_signals(st) == ""


# lhs = "signal lvds_data" (16), name_len = 20
_EXPECTED_SIGNALS = (
    "    signal sys_clk      : std_logic;\n"
    "    signal led          : std_logic_vector(3 downto 0);\n"
    "    signal user_led     : std_logic;\n"
    "    signal ref_clk      : std_logic;\n"
    "    signal lvds_data    : std_logic_vector(2 downto 0);\n"
    "    signal gpio_i       : std_logic_vector(4 downto 0);\n"
    "    signal gpio_o       : std_logic_vector(4 downto 0);\n"
    "    signal gpio_t       : std_logic_vector(4 downto 0);"
)


def test_signals_integration_output() -> None:
    """Full signal set produces the expected signal declaration block."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _generate_vhdl_signals(st) == _EXPECTED_SIGNALS


# ---- _generate_vhdl_ioring_inst --------------------------------------------


def test_ioring_inst_returns_str() -> None:
    """_generate_vhdl_ioring_inst returns a string."""
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
    assert isinstance(_generate_vhdl_ioring_inst(st, "test"), str)


def test_ioring_inst_header() -> None:
    """Entity instantiation header uses the top name with commented generic block on separate lines."""
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
    output = _generate_vhdl_ioring_inst(st, "test")
    lines = output.splitlines()
    assert lines[0] == "    test_io_i0 : entity work.test_io"
    assert lines[1] == "    -- generic map ("
    assert lines[2] == "    -- )"
    assert lines[3] == "    port map ("


def test_ioring_inst_closing() -> None:
    """The instance closes with a 4-space-indented ');'."""
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
    output = _generate_vhdl_ioring_inst(st, "test")
    assert output.splitlines()[-1] == "    );"


def test_ioring_inst_last_port_no_comma() -> None:
    """The last port connection has no trailing comma."""
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
    output = _generate_vhdl_ioring_inst(st, "test")
    port_lines = [ln for ln in output.splitlines() if "=>" in ln]
    assert not port_lines[-1].endswith(",")


def test_ioring_inst_bypass_excluded() -> None:
    """bypass:true signals do not appear in the IO ring instantiation."""
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
    output = _generate_vhdl_ioring_inst(st, "test")
    assert "spare" not in output


def test_ioring_inst_alignment_tab_stop() -> None:
    """When the longest port name lands on a multiple of 4, gap is exactly 1 space.

    'led_pad' is 7 chars; name_len = ((7 // 4) + 1) * 4 = 8.
    The '=>' follows the name field directly, giving a 1-space gap after
    'led_pad' and a 5-space gap after 'led'.
    """
    st = _make_signal_table(
        [
            {
                "name": "led",
                "pins": "A22",
                "direction": "out",
                "buffer": "obuf",
                "iostandard": "LVCMOS18",
            },
        ]
    )
    output = _generate_vhdl_ioring_inst(st, "test")
    # led_pad is the IO ring pad port; led is the fabric-facing port (last, no comma)
    assert "        led_pad => led_pad," in output
    assert "        led     => led" in output


# longest ioring port name = user_led_pad (12), name_len = 16
_EXPECTED_IORING_INST = (
    "    example_io_i0 : entity work.example_io\n"
    "    -- generic map (\n"
    "    -- )\n"
    "    port map (\n"
    "        sys_clk_pad     => sys_clk_pad,\n"
    "        sys_clk         => sys_clk,\n"
    "        led_pad         => led_pad,\n"
    "        led             => led,\n"
    "        user_led_pad    => user_led_pad,\n"
    "        user_led        => user_led,\n"
    "        ref_clk_p       => ref_clk_p,\n"
    "        ref_clk_n       => ref_clk_n,\n"
    "        ref_clk         => ref_clk,\n"
    "        lvds_data_p     => lvds_data_p,\n"
    "        lvds_data_n     => lvds_data_n,\n"
    "        lvds_data       => lvds_data,\n"
    "        gpio_pad        => gpio_pad,\n"
    "        gpio_i          => gpio_i,\n"
    "        gpio_o          => gpio_o,\n"
    "        gpio_t          => gpio_t\n"
    "    );"
)


def test_ioring_inst_integration() -> None:
    """Full signal set produces the expected IO ring instantiation.

    spare is bypass:true and must be absent. name_len = 16 because the longest
    ioring port name is user_led_pad (12); ((12 // 4) + 1) * 4 = 16.
    """
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert _generate_vhdl_ioring_inst(st, "example") == _EXPECTED_IORING_INST


# ---- generate_vhdl_top -----------------------------------------------------

_EXPECTED_TOP = (
    "library ieee;\n"
    "use ieee.std_logic_1164.all;\n"
    "\n"
    "entity example is\n"
    "    -- generic (\n"
    "    -- )\n"
    "    port (\n"
    + _EXPECTED_PORTS
    + "\n"
    + "    );\n"
    + "end entity example;\n"
    + "\n"
    + "architecture rtl of example is\n"
    + "\n"
    + _EXPECTED_SIGNALS
    + "\n"
    + "\n"
    + "begin\n"
    + "\n"
    + _EXPECTED_IORING_INST
    + "\n"
    + "\n"
    + "end architecture rtl;\n"
)


def test_generate_vhdl_top_returns_str() -> None:
    """generate_vhdl_top returns a string."""
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
    assert isinstance(generate_vhdl_top(st, _TEST_META, "test"), str)


def test_generate_vhdl_top_entity_header() -> None:
    """Entity header uses the top name with commented generic block on separate lines."""
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
    output = generate_vhdl_top(st, _TEST_META, "test")
    assert "entity test is" in output
    assert "    -- generic (" in output
    assert "    -- )" in output
    assert "    port (" in output


def test_generate_vhdl_top_end_entity() -> None:
    """end entity line uses the top name."""
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
    output = generate_vhdl_top(st, _TEST_META, "test")
    assert "end entity test;" in output


def test_generate_vhdl_top_architecture_header() -> None:
    """Architecture declaration uses both arch and top names."""
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
    output = generate_vhdl_top(st, _TEST_META, "test")
    assert "architecture rtl of test is" in output
    assert "end architecture rtl;" in output


def test_generate_vhdl_top_ends_with_newline() -> None:
    """Output ends with a trailing newline."""
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
    assert generate_vhdl_top(st, _TEST_META, "test").endswith("\n")


def test_generate_vhdl_top_library_clauses() -> None:
    """Output begins with ieee library and std_logic_1164 use clause."""
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
    output = generate_vhdl_top(st, _TEST_META, "test")
    lines = output.splitlines()
    assert lines[0] == "library ieee;"
    assert lines[1] == "use ieee.std_logic_1164.all;"


def test_generate_vhdl_top_integration() -> None:
    """Full signal set produces the expected complete output."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert generate_vhdl_top(st, _TEST_META, "example") == _EXPECTED_TOP
