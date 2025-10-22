from difflib import unified_diff


def assert_signal_list_equal(
    expected: list[dict[str, str]], actual: list[dict[str, str]]
) -> None:
    """Assert equality of lists of signals before formatting"""

    if len(expected) != len(actual):
        raise AssertionError(
            f"Signal count differs: expected {len(expected)} but actual {len(actual)}"
        )

    for exp, act in zip(expected, actual):
        if exp["name"] != act["name"]:
            raise AssertionError(
                f"Signal names mismatched: expected '{exp['name']}' but actual '{act['name']}'"
            )

        name = exp["name"]

        if exp["type"] != act["type"]:
            raise AssertionError(
                f"Signal '{name}' types mismatched: expected '{exp['type']}' but actual '{act['type']}'"
            )

        if exp["type"] == "std_logic_vector":
            if exp["range"] != act["range"]:
                raise AssertionError(
                    f"Signal '{name}' ranges mismatched: expected '{exp['range']}' but actual '{act['range']}'"
                )
            if exp["range"] is None or act["range"] is None:
                raise AssertionError(
                    f"Signal '{name}' range for 'std_logic_vector' should not be None"
                )
        else:
            if exp["range"] is not None and act["range"] is not None:
                raise AssertionError(
                    f"Signal '{name}' range for 'std_logic' should be None"
                )


def assert_list_equal_with_diff(expected: list, actual: list) -> None:
    """Raise and AssertionError with a unified diff when lists differ"""
    diff = unified_diff(
        expected, actual, fromfile="expected", tofile="actual", lineterm=""
    )
    diff_lines = list(diff)
    if diff_lines:
        raise AssertionError("\n".join(diff_lines))
