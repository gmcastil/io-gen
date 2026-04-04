def _format_port_block(lines: list[str], level: int, lang: str) -> list[str]:
    """Indents a list of port strings and adds the appropriate suffix"""

    if not lines:
        return []
    # A list of port definitions in this context should be a comment line (maybe) followed by a
    # port definition. That means that we should never have a comment as the last line in the input list
    assert not lines[-1].startswith("//") and not lines[-1].startswith("--")

    # Determine indent level
    indent = " " * (level * 4)

    # Determine how to comment and terminate lines of actual HDL
    comment_prefix = "//" if lang == "verilog" else "--"
    port_suffix = "," if lang == "verilog" else ";"

    # Don't put a suffix on the last line in the block of ports
    last_index = len(lines) - 1

    # Now indent the entire list and put commas and semicolons on everything
    # non-comment except the last one.
    result = []
    for index, line in enumerate(lines):
        # Comments only get indented
        if line.startswith(comment_prefix):
            result.append(f"{indent}{line}")
        # Actual port lines get indented and terminated (except for the last one)
        else:
            if index != last_index:
                result.append(f"{indent}{line}{port_suffix}")
            else:
                result.append(f"{indent}{line}")

    return result


def _indent_join(lines: list[str], level: int) -> str:
    """Indents a list of lines and joins them together with a newline"""
    indent = level * f"{'':<4}"
    result = [indent + line for line in lines]
    return "\n".join(result)
