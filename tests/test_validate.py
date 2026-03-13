from textwrap import dedent
import pytest
import yaml
from pathlib import Path

from io_gen import validate, ValidationError
from io_gen.validate import _validate_structural

TMP_YAML = "input.yaml"


def write_yaml(tmp_path: Path, content: str) -> Path:
    """Write YAML in text form to a per-test temporary YAML file"""
    p = tmp_path / TMP_YAML
    p.write_text(dedent(content))
    return p


def load_yaml(content: str) -> dict:
    """Parse a YAML string into a dict without file I/O"""
    return yaml.safe_load(dedent(content))


# ---------------------------------------------------------------------------
# Structural validation
# ---------------------------------------------------------------------------

VALID_STRUCTURAL_CASES = [
    (
        "scalar_pin_explicit_iostandard",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "generate_false",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: reserved_nc
            pins: H24
            generate: false
        """,
    ),
]


@pytest.mark.parametrize(
    "yaml_text",
    [pytest.param(y, id=n) for n, y in VALID_STRUCTURAL_CASES],
)
def test_valid_structural(yaml_text: str) -> None:
    """Check that a valid document passes structural validation"""
    _validate_structural(load_yaml(yaml_text))


INVALID_STRUCTURAL_CASES = [
    (
        "missing_title",
        """
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "missing_direction",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            buffer: ibuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "invalid_buffer_enum",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: in
            buffer: notabuffer
            iostandard: LVCMOS18
        """,
    ),
    (
        "array_pins_missing_width",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: led
            pins: [A22, B22]
            direction: out
            buffer: obuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "scalar_pin_missing_iostandard",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: in
            buffer: ibuf
        """,
    ),
    (
        "scalar_pinset_missing_iostandard",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: ref_clk
            pinset:
              p: H22
              n: H23
            direction: in
            buffer: ibufds
        """,
    ),
    (
        "bypass_with_buffer",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: spare
            pins: J24
            iostandard: LVCMOS18
            direction: out
            buffer: obuf
            bypass: true
        """,
    ),
    (
        "both_pins_and_pinset",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: clk
            pins: G22
            pinset:
              p: H22
              n: H23
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
        """,
    ),
]


@pytest.mark.parametrize(
    "yaml_text",
    [pytest.param(y, id=n) for n, y in INVALID_STRUCTURAL_CASES],
)
def test_invalid_structural(yaml_text: str) -> None:
    """Confirm that structurally invalid YAML raises a ValidationError"""
    with pytest.raises(ValidationError):
        _validate_structural(load_yaml(yaml_text))


# ---------------------------------------------------------------------------
# Integration - validate()
# ---------------------------------------------------------------------------

VALID_INTEGRATION_CASES = [
    (
        "scalar_pin_explicit_iostandard",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
        """,
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "direction": "in",
                    "buffer": "ibuf",
                    "iostandard": "LVCMOS18",
                }
            ],
        },
    ),
    (
        "generate_false",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: reserved_nc
            pins: H24
            generate: false
        """,
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "signals": [
                {
                    "name": "reserved_nc",
                    "pins": "H24",
                    "generate": False,
                }
            ],
        },
    ),
]


@pytest.mark.parametrize(
    "yaml_text, expected",
    [pytest.param(y, e, id=n) for n, y, e in VALID_INTEGRATION_CASES],
)
def test_valid_integration(tmp_path: Path, yaml_text: str, expected: dict) -> None:
    """Check that valid YAML is parsed and returned correctly by validate()"""
    doc = validate(write_yaml(tmp_path, yaml_text))
    assert doc == expected
