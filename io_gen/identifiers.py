import re

# Per the LRM, a simple identifier shall be any sequence of letters, digits,
# dollar signs ($), and underscore characters (_). Because identifiers need
# to be used for port names, which get pulled into XDC constraints, we
# restrict here by disallowing dollar signs ($) in the identifier

_VERILOG_ID = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _is_valid_verilog_identifier(name: str) -> bool:
    """Returns True if identifier name is a valid simple identifier"""
    return bool(_VERILOG_ID.match(name))


def _is_valid_vhdl_identifier(name: str) -> bool:
    return True
