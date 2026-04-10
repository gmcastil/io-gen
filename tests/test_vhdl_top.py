import pytest

from io_gen.tables import SignalTable
from io_gen.tables.signal_table import _build_signal_table

from io_gen.generate.vhdl_top import (
    _generate_vhdl_ports,
    _generate_vhdl_signals,
    _generate_vhdl_ioring_inst,
    generate_vhdl_top,
)


def _make_signal_table(signals: list) -> SignalTable:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    return _build_signal_table(doc)


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


# Port declarations are checked as substrings. name_len is driven by the longest
# port name in the table - single-signal tables produce their own alignment.

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
        # longest port name = sys_clk_pad (11), name_len = 16
        "sys_clk_pad     : in    std_logic",
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
        # longest port name = led_pad (7), name_len = 12
        "led_pad     : out   std_logic_vector(3 downto 0)",
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
        # longest port name = ref_clk_p or ref_clk_n (9), name_len = 12
        "ref_clk_p   : in    std_logic",
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
        "ref_clk_n   : in    std_logic",
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
        # longest port name = lvds_data_p or lvds_data_n (11), name_len = 16
        "lvds_data_p     : out   std_logic_vector(2 downto 0)",
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
        "lvds_data_n     : out   std_logic_vector(2 downto 0)",
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
        # longest port name = gpio_pad (8), name_len = 12
        "gpio_pad    : inout std_logic_vector(4 downto 0)",
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
        # longest port name = spare_pad (9), name_len = 12
        "spare_pad   : out   std_logic",
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
        # longest port name = data_pad (8), name_len = 12
        "data_pad    : out   std_logic_vector(15 downto 0)",
    ),
]


@pytest.mark.parametrize(
    "sig, expected_decl",
    [pytest.param(s, d, id=n) for n, s, d in PORT_DECL_CASES],
)
def test_port_decl_in_output(sig: dict, expected_decl: str) -> None:
    """The correct port declaration appears in the output for each signal type."""
    st = _make_signal_table([sig])
    assert expected_decl in _generate_vhdl_ports(st)


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
    assert "-- 125 MHz system clock input" in _generate_vhdl_ports(st)


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
    output = _generate_vhdl_ports(st)
    last_line = [ln for ln in output.splitlines() if ln.strip()][-1]
    assert not last_line.endswith(";")


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

# Signal declarations are checked as substrings. name_len is driven by the
# longest net name in the table.

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
        # longest net name = sys_clk (7), name_len = 9
        ["    signal sys_clk   : std_logic;"],
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
        # longest net name = led (3), name_len = 5
        ["    signal led   : std_logic_vector(3 downto 0);"],
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
        # longest net name = ref_clk (7), name_len = 9
        ["    signal ref_clk   : std_logic;"],
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
        # longest net name = lvds_data (9), name_len = 13
        ["    signal lvds_data    : std_logic_vector(2 downto 0);"],
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
        # longest net name = gpio_i/gpio_o/gpio_t (6), name_len = 9
        [
            "    signal gpio_i   : std_logic;",
            "    signal gpio_o   : std_logic;",
            "    signal gpio_t   : std_logic;",
        ],
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
        [
            "    signal gpio_i   : std_logic_vector(2 downto 0);",
            "    signal gpio_o   : std_logic_vector(2 downto 0);",
            "    signal gpio_t   : std_logic_vector(2 downto 0);",
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
        ["    signal led   : std_logic_vector(0 downto 0);"],
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
            "    signal gpio_i   : std_logic_vector(0 downto 0);",
            "    signal gpio_o   : std_logic_vector(0 downto 0);",
            "    signal gpio_t   : std_logic_vector(0 downto 0);",
        ],
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
        # longest net name = data (4), name_len = 5
        ["    signal data   : std_logic_vector(15 downto 0);"],
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
        [
            "    signal data_i   : std_logic_vector(15 downto 0);",
            "    signal data_o   : std_logic_vector(15 downto 0);",
            "    signal data_t   : std_logic_vector(15 downto 0);",
        ],
    ),
]


@pytest.mark.parametrize(
    "sig, expected_lines",
    [pytest.param(s, e, id=n) for n, s, e in SIGNAL_DECL_CASES],
)
def test_signal_decl_in_output(sig: dict, expected_lines: list[str]) -> None:
    """The correct signal declaration(s) appear in the output for each signal type."""
    st = _make_signal_table([sig])
    output = _generate_vhdl_signals(st)
    for line in expected_lines:
        assert line in output


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


# longest net name = lvds_data (9), name_len = 13
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
    """Instance label, commented generic map, and port map keyword appear on separate lines."""
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
    assert lines[2] == "    --    )"
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
    """The '=>' lands at the next tab stop column.

    'led_pad' is 7 chars; 8 (indent) + 7 + 1 (min space) = 16, which is already
    a multiple of 4. name_len = 8 (next_tab 16 - indent 8 = 8).
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
    assert "        led_pad  => led_pad," in output
    assert "        led      => led" in output


# longest ioring port name = user_led_pad (12), name_len = 16
_EXPECTED_IORING_INST = (
    "    example_io_i0 : entity work.example_io\n"
    "    -- generic map (\n"
    "    --    )\n"
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

    spare is bypass:true and must be absent. name_len=16 because the longest
    port name is user_led_pad (12); 8 (indent) + 12 + 1 (min space) = 21,
    rounded up to next multiple of 4 gives 24, so name_len = 24 - 8 = 16.
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
    "    --    )\n"
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
    assert isinstance(generate_vhdl_top(st, "test", "rtl"), str)


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
    output = generate_vhdl_top(st, "test", "rtl")
    assert "entity test is" in output
    assert "    -- generic (" in output
    assert "    --    )" in output
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
    output = generate_vhdl_top(st, "test", "rtl")
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
    output = generate_vhdl_top(st, "test", "rtl")
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
    assert generate_vhdl_top(st, "test", "rtl").endswith("\n")


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
    output = generate_vhdl_top(st, "test", "rtl")
    lines = output.splitlines()
    assert lines[0] == "library ieee;"
    assert lines[1] == "use ieee.std_logic_1164.all;"


def test_generate_vhdl_top_integration() -> None:
    """Full signal set produces output matching example.vhd."""
    st = _make_signal_table(_INTEGRATION_SIGNALS)
    assert generate_vhdl_top(st, "example", "rtl") == _EXPECTED_TOP
