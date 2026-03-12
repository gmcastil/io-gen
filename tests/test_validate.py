from textwrap import dedent
import pytest
from pathlib import Path
from io_gen import validate, ValidationError

TMP_YAML = "input.yaml"


def write_yaml(tmp_path: Path, content: str) -> Path:
    """Write YAML in text form to a per-test temporary YAML file"""
    p = tmp_path / TMP_YAML
    p.write_text(dedent(content))
    return p


# Valid structual cases
VALID_CASES = [
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
        "scalar_pin_bank_inheritance",
        """
        title: Test
        part: xc7k325tffg900-2
        banks:
          34:
            iostandard: LVCMOS18
            performance: HR
        signals:
          - name: sys_clk
            pins: G22
            bank: 34
            direction: in
            buffer: ibuf
        """,
        {
            "title": "Test",
            "part": "xc7k325tffg900-2",
            "banks": {
                34: {
                    "iostandard": "LVCMOS18",
                    "performance": "HR",
                }
            },
            "signals": [
                {
                    "name": "sys_clk",
                    "pins": "G22",
                    "bank": 34,
                    "direction": "in",
                    "buffer": "ibuf",
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
    [pytest.param(y, e, id=n) for n, y, e in VALID_CASES],
)
def test_valid_structural_yaml(tmp_path: Path, yaml_text: str, expected: dict) -> None:
    """Check that structurally correct YAML is returned correctly"""
    doc = validate(write_yaml(tmp_path, yaml_text))
    assert doc == expected


# Invalid structural cases
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
def test_invalid_structural_yaml(tmp_path: Path, yaml_text: str) -> None:
    """Confirm that structurally invalid YAML raises a ValidationError"""
    with pytest.raises(ValidationError):
        validate(write_yaml(tmp_path, yaml_text))


# Invalid semantic cases
INVALID_SEMANTIC_CASES = [
    (
        "duplicate_signal_names",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
          - name: sys_clk
            pins: H22
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "duplicate_pins",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
          - name: sys_rst
            pins: G22
            direction: in
            buffer: ibuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "duplicate_pinset",
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
            iostandard: LVDS
          - name: aux_clk
            pinset:
              p: H22
              n: H23
            direction: in
            buffer: ibufds
            iostandard: LVDS
        """,
    ),
    (
        "scalar_no_iostandard_no_bank",
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
        "no_banks_map_signal_references_bank",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            bank: 34
            direction: in
            buffer: ibuf
        """,
    ),
    (
        "bank_not_in_banks_map",
        """
        title: Test
        part: xc7k325tffg900-2
        banks:
          34:
            iostandard: LVCMOS18
            performance: HR
        signals:
          - name: sys_clk
            pins: G22
            bank: 99
            direction: in
            buffer: ibuf
        """,
    ),
    (
        "pins_width_too_large",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: led
            pins: [X0]
            width: 2
            direction: out
            buffer: obuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "pins_width_too_small",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: led
            pins: [X0, X1]
            width: 1
            direction: out
            buffer: obuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "ibuf_wrong_direction",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: sys_clk
            pins: G22
            direction: out
            buffer: ibuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "obuf_wrong_direction",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: led
            pins: G22
            direction: in
            buffer: obuf
            iostandard: LVCMOS18
        """,
    ),
    (
        "ibufds_wrong_direction",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: ref_clk
            pinset:
              p: H22
              n: H23
            direction: out
            buffer: ibufds
            iostandard: LVDS
        """,
    ),
    (
        "obufds_wrong_direction",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: lvds_data
            pinset:
              p: H22
              n: H23
            direction: in
            buffer: obufds
            iostandard: LVDS
        """,
    ),
    (
        "pinset_p_scalar_n_array",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: ref_clk
            pinset:
              p: H22
              n: [H23]
            direction: in
            buffer: ibufds
            iostandard: LVDS
        """,
    ),
    (
        "pinset_p_n_length_mismatch",
        """
        title: Test
        part: xc7k325tffg900-2
        signals:
          - name: lvds_data
            pinset:
              p: [AA1, AB1]
              n: [AA2]
            width: 2
            direction: out
            buffer: obufds
            iostandard: LVDS
        """,
    ),
    (
        "infer_with_non_inferrable_buffer",
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
            infer: true
            iostandard: LVDS
        """,
    ),
]


@pytest.mark.parametrize(
    "yaml_text",
    [pytest.param(y, id=n) for n, y in INVALID_SEMANTIC_CASES],
)
def test_invalid_semantic_yaml(tmp_path: Path, yaml_text: str) -> None:
    """Confirm that semantically invalid YAML raises a ValidationError"""
    with pytest.raises(ValidationError):
        validate(write_yaml(tmp_path, yaml_text))
