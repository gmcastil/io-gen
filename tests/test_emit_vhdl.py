from pathlib import Path
import pytest

from tests.helpers import assert_signal_list_equal
from tests.helpers import load_signal_table
from tests.helpers import read_vhdl_signals

from io_gen.emit_vhdl import emit_vhdl_signals

# VHDL test cases are stored at this location and require that the following files are present in
# that directory:
#
#   signal_table.json - The appropriate signal table data structure to test against
#   top.vhdl.golden - The expected VHDL entity declaration file to generate from the signal table
#   signals.vhdl.golden - The expected signal definitions
#
EMITTER_CASES = Path("tests/emitter_cases")
CASES = sorted(p for p in EMITTER_CASES.iterdir() if p.is_dir())


@pytest.mark.parametrize("case", CASES, ids=[p.name for p in CASES])
def test_vhdl_signals_cases(case: Path):
    """Test a single VHDL signal emitter case"""

    # Load the signal table from the JSON file
    sig_table = load_signal_table(case / "signal_table.json")

    # Retrieve expected signal declarations for the specified test case
    expected = read_vhdl_signals(case / "signals.vhdl.golden")

    # Retrieve the actual signal declarations emitted
    actual = emit_vhdl_signals(sig_table)

    assert_signal_list_equal(expected, actual)
