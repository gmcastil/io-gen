def indent_join(lines: list[str], level: int = 1, char: str = "\n") -> str:
    """Indents a list of lines and joins them together (default to newline)"""
    return char.join(indent_strings(lines, level))


def indent_strings(lines: list[str], level: int = 1) -> list[str]:
    """Indents a list of strings and returns without joining"""
    indent = level * "    "
    return [f"{indent}{line}" for line in lines]
