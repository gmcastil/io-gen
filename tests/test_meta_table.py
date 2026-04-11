import pytest

from io_gen.tables import MetaTable
from io_gen.tables.meta_table import build_meta_table

# A few details - the first string is the test name, second is the actual dict from JSON,
# the third is the expected title, and the fourth is the expected part number. The
# signals are irrelevant because the MetaTable doesn't need those.
META_TABLE_CASES = [
    (
        "basic",
        {
            "title": "Example Design",
            "part": "xc7k325tffg900-2",
            "signals": [],
        },
        "Example Design",
        "xc7k325tffg900-2",
        None,
    ),
    (
        "different_part",
        {
            "title": "Basys 3 Test",
            "part": "xc7a35tcpg236-1",
            "signals": [],
        },
        "Basys 3 Test",
        "xc7a35tcpg236-1",
        None,
    ),
    (
        "with_architecture",
        {
            "title": "Example Design",
            "part": "xc7k325tffg900-2",
            "architecture": "rtl",
            "signals": [],
        },
        "Example Design",
        "xc7k325tffg900-2",
        "rtl",
    ),
]


@pytest.mark.parametrize(
    "doc, expected_title, expected_part, expected_architecture",
    [pytest.param(d, t, p, a, id=n) for n, d, t, p, a in META_TABLE_CASES],
)
def test_build_meta_table(
    doc: dict,
    expected_title: str,
    expected_part: str,
    expected_architecture: str | None,
) -> None:
    """build_meta_table returns a MetaTable with title, part, and architecture from the doc"""
    result = build_meta_table(doc)
    assert isinstance(result, MetaTable)
    assert result.title == expected_title
    assert result.part == expected_part
    assert result.architecture == expected_architecture
