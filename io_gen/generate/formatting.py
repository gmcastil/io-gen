def _format_port_block(lines: list[str], level: int, lang: str) -> list[str]:
    """Indents a list of port strings and adds the appropriate suffix"""

    if lang == "verilog":
        for index, line in enumerate(lines):
            if line.startswith("#"):
                lines[index] = line.rjust(12)
            else:
                if index != len(lines) - 1:
                    lines[ = f"{line},"

    return lines
