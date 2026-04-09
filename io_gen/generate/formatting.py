def _indent_join(lines: list[str], level: int, char: str = "\n") -> str:
    """Indents a list of lines and joins them together (default to newline)"""
    indent = level * f"{'':<4}"
    result = [indent + line for line in lines]
    return char.join(result)
