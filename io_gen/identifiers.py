import re

# Per the LRM, a simple identifier shall be any sequence of letters, digits,
# dollar signs ($), and underscore characters (_). Because identifiers need
# to be used for port names, which get pulled into XDC constraints, we
# restrict here by disallowing dollar signs ($) in the identifier

_VERILOG_ID = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# Per Ashenden, a basic identifier
# - may only contain alphabetic letters (A-Z, a-z), decimal digits (0-9),
#   and the underline character (_);
# - must start with an alphabetic letter;
# - may not end with an underline character; and
# - may not include two successive underline characters.
#
# An underscore can only appear in the string if it is immediately consumed
# together with the character after it.
_VHDL_ID = re.compile(r"^[a-zA-Z]([a-zA-Z0-9]|_[a-zA-Z0-9])*$")


def is_valid_verilog_identifier(name: str) -> bool:
    """Returns True if identifier name is a valid simple identifier"""
    return bool(_VERILOG_ID.match(name))


def is_valid_vhdl_identifier(name: str) -> bool:
    """Returns True if identifier name is a valid basic identifier"""
    return bool(_VHDL_ID.match(name))
