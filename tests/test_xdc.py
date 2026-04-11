import pytest

from io_gen.generate.xdc import generate_xdc
from io_gen.tables.pin_table import build_pin_table
from io_gen.tables.signal_table import build_signal_table


def _make_tables(signals: list) -> tuple:
    doc = {"title": "Test", "part": "xc7k325tffg900-2", "signals": signals}
    st = build_signal_table(doc)
    pt = build_pin_table(st)
    return st, pt


def test_generate_xdc_returns_str() -> None:
    """generate_xdc returns a string."""
    st, pt = _make_tables(
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
    assert isinstance(generate_xdc(st, pt), str)


# Each case: (name, sig, expected_port). expected_port must appear verbatim in
# the output (inside a get_ports call).

PORT_NAME_CASES = [
    (
        "scalar_single_ended",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "sys_clk_pad",
    ),
    (
        "bus_single_ended_index_0",
        {
            "name": "led",
            "pins": ["A22", "B22"],
            "width": 2,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "{led_pad[0]}",
    ),
    (
        "bus_single_ended_index_1",
        {
            "name": "led",
            "pins": ["A22", "B22"],
            "width": 2,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "{led_pad[1]}",
    ),
    (
        "scalar_differential_p",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        "ref_clk_p",
    ),
    (
        "scalar_differential_n",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        "ref_clk_n",
    ),
    (
        "bus_differential_p_index_0",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]},
            "width": 2,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "{lvds_data_p[0]}",
    ),
    (
        "bus_differential_n_index_1",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]},
            "width": 2,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "{lvds_data_n[1]}",
    ),
    (
        "one_element_bus_single_ended",
        {
            "name": "cs_n",
            "pins": ["A22"],
            "width": 1,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "{cs_n_pad[0]}",
    ),
    (
        "one_element_bus_differential_p",
        {
            "name": "clk_out",
            "pinset": {"p": ["H22"], "n": ["H23"]},
            "width": 1,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "{clk_out_p[0]}",
    ),
    (
        "one_element_bus_differential_n",
        {
            "name": "clk_out",
            "pinset": {"p": ["H22"], "n": ["H23"]},
            "width": 1,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "{clk_out_n[0]}",
    ),
]


@pytest.mark.parametrize(
    "sig, expected_port",
    [pytest.param(s, p, id=n) for n, s, p in PORT_NAME_CASES],
)
def test_port_name_in_output(sig: dict, expected_port: str) -> None:
    """The correct get_ports name appears in the output for each signal type."""
    st, pt = _make_tables([sig])
    assert expected_port in generate_xdc(st, pt)


# ---------------------------------------------------------------------------
# DIRECTION constraint
# ---------------------------------------------------------------------------

DIRECTION_CASES = [
    (
        "scalar_se_in",
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
        },
        "set_property DIRECTION IN [get_ports sys_clk_pad]",
    ),
    (
        "scalar_se_out",
        {
            "name": "led_en",
            "pins": "A22",
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "set_property DIRECTION OUT [get_ports led_en_pad]",
    ),
    (
        "scalar_se_inout",
        {
            "name": "gpio",
            "pins": "E22",
            "direction": "inout",
            "buffer": "iobuf",
            "iostandard": "LVCMOS18",
        },
        "set_property DIRECTION INOUT [get_ports gpio_pad]",
    ),
    (
        "bus_se_out",
        {
            "name": "led",
            "pins": ["A22", "B22"],
            "width": 2,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
        },
        "set_property DIRECTION OUT [get_ports {led_pad[1]}]",
    ),
    (
        "scalar_diff_in",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        "set_property DIRECTION IN [get_ports ref_clk_p]",
    ),
    (
        "scalar_diff_in_n_side",
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
        },
        "set_property DIRECTION IN [get_ports ref_clk_n]",
    ),
    (
        "bus_diff_out",
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]},
            "width": 2,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
        },
        "set_property DIRECTION OUT [get_ports {lvds_data_p[0]}]",
    ),
    (
        "bypass_out",
        {
            "name": "spare",
            "pins": "J24",
            "direction": "out",
            "iostandard": "LVCMOS18",
            "bypass": True,
        },
        "set_property DIRECTION OUT [get_ports spare_pad]",
    ),
]


@pytest.mark.parametrize(
    "sig, expected_line",
    [pytest.param(s, l, id=n) for n, s, l in DIRECTION_CASES],
)
def test_direction_in_output(sig: dict, expected_line: str) -> None:
    """A DIRECTION constraint is emitted for every port."""
    st, pt = _make_tables([sig])
    assert expected_line in generate_xdc(st, pt)


def test_xdc_comment_emitted() -> None:
    """comment.xdc is emitted as a # line before the signal's constraints."""
    st, pt = _make_tables(
        [
            {
                "name": "sys_clk",
                "pins": "G22",
                "direction": "in",
                "buffer": "ibuf",
                "iostandard": "LVCMOS18",
                "comment": {"xdc": "125 MHz system clock"},
            }
        ]
    )
    assert "# 125 MHz system clock" in generate_xdc(st, pt)


def test_no_comment_produces_no_hash_line() -> None:
    """A signal with no comment.xdc produces no # line in the output."""
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
    assert "#" not in generate_xdc(st, pt)


def test_bypass_true_included() -> None:
    """bypass:true signals still appear in the XDC."""
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
    assert "spare_pad" in generate_xdc(st, pt)


_INTEGRATION_DOC = {
    "title": "Test",
    "part": "xc7k325tffg900-2",
    "signals": [
        {
            "name": "sys_clk",
            "pins": "G22",
            "direction": "in",
            "buffer": "ibuf",
            "iostandard": "LVCMOS18",
            "comment": {"xdc": "125 MHz system clock"},
        },
        {
            "name": "led",
            "pins": ["A22", "B22"],
            "width": 2,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "comment": {"xdc": "User LEDs"},
        },
        {
            "name": "ref_clk",
            "pinset": {"p": "H22", "n": "H23"},
            "direction": "in",
            "buffer": "ibufds",
            "iostandard": "LVDS",
            "comment": {"xdc": "200 MHz reference clock"},
        },
        {
            "name": "lvds_data",
            "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]},
            "width": 2,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
            "comment": {"xdc": "LVDS data outputs"},
        },
        {
            "name": "cs_n",
            "pins": ["E22"],
            "width": 1,
            "direction": "out",
            "buffer": "obuf",
            "iostandard": "LVCMOS18",
            "comment": {"xdc": "Chip select"},
        },
        {
            "name": "sync_clk",
            "pinset": {"p": ["F22"], "n": ["F23"]},
            "width": 1,
            "direction": "out",
            "buffer": "obufds",
            "iostandard": "LVDS",
            "comment": {"xdc": "Sync clock"},
        },
        {
            "name": "spare",
            "pins": "J24",
            "direction": "out",
            "iostandard": "LVCMOS18",
            "bypass": True,
            "comment": {"xdc": "Spare output pin"},
        },
    ],
}

_EXPECTED_XDC = """\
# 125 MHz system clock
set_property PACKAGE_PIN G22 [get_ports sys_clk_pad]
set_property IOSTANDARD LVCMOS18 [get_ports sys_clk_pad]
set_property DIRECTION IN [get_ports sys_clk_pad]

# User LEDs
set_property PACKAGE_PIN A22 [get_ports {led_pad[0]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_pad[0]}]
set_property DIRECTION OUT [get_ports {led_pad[0]}]
set_property PACKAGE_PIN B22 [get_ports {led_pad[1]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_pad[1]}]
set_property DIRECTION OUT [get_ports {led_pad[1]}]

# 200 MHz reference clock
set_property PACKAGE_PIN H22 [get_ports ref_clk_p]
set_property IOSTANDARD LVDS [get_ports ref_clk_p]
set_property DIRECTION IN [get_ports ref_clk_p]
set_property PACKAGE_PIN H23 [get_ports ref_clk_n]
set_property IOSTANDARD LVDS [get_ports ref_clk_n]
set_property DIRECTION IN [get_ports ref_clk_n]

# LVDS data outputs
set_property PACKAGE_PIN AA1 [get_ports {lvds_data_p[0]}]
set_property IOSTANDARD LVDS [get_ports {lvds_data_p[0]}]
set_property DIRECTION OUT [get_ports {lvds_data_p[0]}]
set_property PACKAGE_PIN AA2 [get_ports {lvds_data_n[0]}]
set_property IOSTANDARD LVDS [get_ports {lvds_data_n[0]}]
set_property DIRECTION OUT [get_ports {lvds_data_n[0]}]
set_property PACKAGE_PIN AB1 [get_ports {lvds_data_p[1]}]
set_property IOSTANDARD LVDS [get_ports {lvds_data_p[1]}]
set_property DIRECTION OUT [get_ports {lvds_data_p[1]}]
set_property PACKAGE_PIN AB2 [get_ports {lvds_data_n[1]}]
set_property IOSTANDARD LVDS [get_ports {lvds_data_n[1]}]
set_property DIRECTION OUT [get_ports {lvds_data_n[1]}]

# Chip select
set_property PACKAGE_PIN E22 [get_ports {cs_n_pad[0]}]
set_property IOSTANDARD LVCMOS18 [get_ports {cs_n_pad[0]}]
set_property DIRECTION OUT [get_ports {cs_n_pad[0]}]

# Sync clock
set_property PACKAGE_PIN F22 [get_ports {sync_clk_p[0]}]
set_property IOSTANDARD LVDS [get_ports {sync_clk_p[0]}]
set_property DIRECTION OUT [get_ports {sync_clk_p[0]}]
set_property PACKAGE_PIN F23 [get_ports {sync_clk_n[0]}]
set_property IOSTANDARD LVDS [get_ports {sync_clk_n[0]}]
set_property DIRECTION OUT [get_ports {sync_clk_n[0]}]

# Spare output pin
set_property PACKAGE_PIN J24 [get_ports spare_pad]
set_property IOSTANDARD LVCMOS18 [get_ports spare_pad]
set_property DIRECTION OUT [get_ports spare_pad]
"""


def test_integration_output() -> None:
    """Full document produces the expected XDC string."""
    st = build_signal_table(_INTEGRATION_DOC)
    pt = build_pin_table(st)
    assert generate_xdc(st, pt) == _EXPECTED_XDC


def test_generate_xdc_ends_with_newline() -> None:
    """Output ends with a trailing newline."""
    st, pt = _make_tables(
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
    assert generate_xdc(st, pt).endswith("\n")
