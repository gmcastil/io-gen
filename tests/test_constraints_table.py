import pytest

from io_gen.tables import ConstraintsTable
from io_gen.tables.constraints_table import build_constraints_table

# ---------------------------------------------------------------------------
# build_constraints_table
# ---------------------------------------------------------------------------

CONSTRAINTS_TABLE_CASES = [
    (
        "vcco_3v3",
        {
            "title": "Test",
            "part": "xc7a35tcpg236-1",
            "constraints": {
                "config_voltage": 3.3,
                "cfgbvs": "VCCO",
            },
            "signals": [],
        },
        3.3,
        "VCCO",
    ),
    (
        "vcco_2v5",
        {
            "title": "Test",
            "part": "xc7a35tcpg236-1",
            "constraints": {
                "config_voltage": 2.5,
                "cfgbvs": "VCCO",
            },
            "signals": [],
        },
        2.5,
        "VCCO",
    ),
    (
        "gnd_1v8",
        {
            "title": "Test",
            "part": "xc7a35tcpg236-1",
            "constraints": {
                "config_voltage": 1.8,
                "cfgbvs": "GND",
            },
            "signals": [],
        },
        1.8,
        "GND",
    ),
    (
        "gnd_1v5",
        {
            "title": "Test",
            "part": "xc7a35tcpg236-1",
            "constraints": {
                "config_voltage": 1.5,
                "cfgbvs": "GND",
            },
            "signals": [],
        },
        1.5,
        "GND",
    ),
]


@pytest.mark.parametrize(
    "doc, expected_config_voltage, expected_cfgbvs",
    [pytest.param(d, v, b, id=n) for n, d, v, b in CONSTRAINTS_TABLE_CASES],
)
def test_build_constraints_table(
    doc: dict,
    expected_config_voltage: float,
    expected_cfgbvs: str,
) -> None:
    """build_constraints_table returns a ConstraintsTable with config_voltage and cfgbvs from the doc"""
    result = build_constraints_table(doc)
    assert isinstance(result, ConstraintsTable)
    assert result.config_voltage == expected_config_voltage
    assert result.cfgbvs == expected_cfgbvs
