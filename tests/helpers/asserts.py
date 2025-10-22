from .util import unified_diff


def assert_equal_with_diff(
    expected: list[str], actual: list[str], fromfile="expected", tofile="actual"
) -> None:
    """Raise and AssertionError with a unified diff when text differs"""
    diff = unified_diff(expected, actual, fromfile=fromfile, tofile=tofile)
    if diff:
        raise AssertionError(diff)
