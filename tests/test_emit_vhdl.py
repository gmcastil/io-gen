from pathlib import Path
import pytest

# VHDL test cases are stored at this location and require that the following files are present in
# that directory:
#
#   top.vhdl.golden - The expected VHDL entity declaration file to generate from the pin table
#   signals.vhdl.golden - The expected signal definitions
#

EMITTER_CASES = Path("tests/emitter_cases")
CASES = sorted(p for p in EMITTER_CASES.iterdir() if p.is_dir())


@pytest.mark.parametrize("case", CASES, ids=[p.name for p in CASES])
def test_vhdl_signals_cases(case: Path):
    """Test a single VHDL signal emitter case"""
