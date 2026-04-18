import pytest

from io_gen.identifiers import is_valid_verilog_identifier, is_valid_vhdl_identifier


# ---------------------------------------------------------------------------
# Valid Verilog identifiers
# ---------------------------------------------------------------------------

VALID_VERILOG_CASES = [
    ("letter_start", "shiftreg_a"),
    ("underscore_start", "_bus3"),
    ("all_caps", "SYS_CLK"),
    ("mixed_case", "busA_index"),
    ("single_letter", "a"),
    ("single_underscore", "_"),
    ("digits_in_body", "sig0"),
]

INVALID_VERILOG_CASES = [
    ("digit_start", "0sig"),
    ("dollar_start", "$sig"),
    ("hyphen", "sys-clk"),
    ("space", "sys clk"),
    ("empty_string", ""),
    ("dot", "a.b"),
    ("at_sign", "@clk"),
    # These are actually valid cases, but we reject identifiers with ($) in them
    ("with_dollar", "n$657"),
    ("dollar_in_body", "error_condition$1"),
]


@pytest.mark.parametrize(
    "name",
    [pytest.param(n, id=label) for label, n in VALID_VERILOG_CASES],
)
def test_valid_verilog_identifier(name: str) -> None:
    assert is_valid_verilog_identifier(name) is True


@pytest.mark.parametrize(
    "name",
    [pytest.param(n, id=label) for label, n in INVALID_VERILOG_CASES],
)
def test_invalid_verilog_identifier(name: str) -> None:
    assert is_valid_verilog_identifier(name) is False


# ---------------------------------------------------------------------------
# Valid VHDL identifiers
# ---------------------------------------------------------------------------

VALID_VHDL_CASES = [
    ("single_letter", "a"),
    ("all_lower", "clk"),
    ("all_caps", "SYS_CLK"),
    ("mixed_case", "data_in"),
    ("trailing_digit", "signal_1"),
    ("multiple_underscores", "A_B_C"),
]

INVALID_VHDL_CASES = [
    ("digit_start", "0clk"),
    ("underscore_start", "_clk"),
    ("trailing_underscore", "clk_"),
    ("consecutive_underscores", "sys__clk"),
    ("empty_string", ""),
    ("hyphen", "sys-clk"),
    ("dollar", "clk_1$"),
    ("space", "clk 1"),
]


@pytest.mark.parametrize(
    "name",
    [pytest.param(n, id=label) for label, n in VALID_VHDL_CASES],
)
def test_valid_vhdl_identifier(name: str) -> None:
    assert is_valid_vhdl_identifier(name) is True


@pytest.mark.parametrize(
    "name",
    [pytest.param(n, id=label) for label, n in INVALID_VHDL_CASES],
)
def test_invalid_vhdl_identifier(name: str) -> None:
    assert is_valid_vhdl_identifier(name) is False
