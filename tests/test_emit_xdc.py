from pathlib import Path
import pytest

from tests.helpers import assert_equal_with_diff
from tests.helpers import load_pin_table
from tests.helpers import read_golden_lines

from io_gen.emit_xdc import emit_xdc_constraints

# XDC test cases are stored at this location and require that the following files are present in
# that directory:
#
#   pin_table.json  - The appropriate pin table data structure to test again
#   top.xdc.golden  - The expected XDC file to generate from the pin table
#
EMITTER_CASES = Path("tests/emitter_cases")
CASES = sorted(p for p in EMITTER_CASES.iterdir() if p.is_dir())


@pytest.mark.parametrize("case", CASES, ids=[p.name for p in CASES])
def test_xdc_cases(case: Path):
    """Test a single XDC emitter case"""

    # Load the pin table from the JSON file using the helper function (since we aren't using
    # just list[dict[str, Any]] and are using dataclasses in our pin table, we need to assemble
    # it properly.
    pin_table = load_pin_table(case / "pin_table.json")

    # Retrieve expected XDC output from the specified test case
    expected = read_golden_lines(case / "top.xdc.golden")

    # Retrieve the actual emitted XDC from the emitter function
    actual = emit_xdc_constraints(pin_table)

    assert_equal_with_diff(
        expected, actual, fromfile=f"{case.name}/expected", tofile=f"{case.name}/actual"
    )
