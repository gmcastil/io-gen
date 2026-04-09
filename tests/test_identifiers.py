import pytest

from io_gen.identifiers import _is_valid_verilog_identifier


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
    assert _is_valid_verilog_identifier(name) is True


@pytest.mark.parametrize(
    "name",
    [pytest.param(n, id=label) for label, n in INVALID_VERILOG_CASES],
)
def test_invalid_verilog_identifier(name: str) -> None:
    assert _is_valid_verilog_identifier(name) is False
