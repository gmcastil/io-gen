from textwrap import dedent
import pytest
import yaml
from pathlib import Path

from io_gen import validate, ValidationError
from io_gen.validate import (
    _validate_structural,
    _check_unique_signal_names,
    _check_unique_pins,
    _check_pinset_array_mismatch,
    _check_pins_array_width_match,
    _check_pinset_array_width_match,
    _check_buffer_direction,
    _check_buffer_strategy_match,
    _check_buffer_infer_bypass_mismatch,
    _check_buffer_inferable,
)

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
# Semantic validation - _check_unique_signal_names
# ---------------------------------------------------------------------------

VALID_UNIQUE_SIGNAL_NAMES = [
    (
        "single_signal",
        [{"name": "sys_clk"}],
    ),
    (
        "multiple_unique_names",
        [{"name": "sys_clk"}, {"name": "led"}, {"name": "ref_clk"}],
    ),
]


@pytest.mark.parametrize(
    "signals",
    [pytest.param(s, id=n) for n, s in VALID_UNIQUE_SIGNAL_NAMES],
)
def test_valid_unique_signal_names(signals: list[dict]) -> None:
    """Check that a list of signals with unique names passes"""
    _check_unique_signal_names(signals)


INVALID_UNIQUE_SIGNAL_NAMES = [
    (
        "duplicate_names",
        [{"name": "sys_clk"}, {"name": "sys_clk"}],
    ),
    (
        "duplicate_among_many",
        [{"name": "sys_clk"}, {"name": "led"}, {"name": "sys_clk"}],
    ),
]


@pytest.mark.parametrize(
    "signals",
    [pytest.param(s, id=n) for n, s in INVALID_UNIQUE_SIGNAL_NAMES],
)
def test_invalid_unique_signal_names(signals: list[dict]) -> None:
    """Confirm that duplicate signal names raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_unique_signal_names(signals)


# ---------------------------------------------------------------------------
# Semantic validation - _check_unique_pins
# ---------------------------------------------------------------------------

VALID_UNIQUE_PINS = [
    (
        "single_scalar_pin",
        [{"name": "sys_clk", "pins": "G22"}],
    ),
    (
        "multiple_signals_unique_scalar_pins",
        [{"name": "sys_clk", "pins": "G22"}, {"name": "sys_rst", "pins": "H22"}],
    ),
    (
        "unique_array_pins",
        [{"name": "sys_clk", "pins": "G22"}, {"name": "led", "pins": ["A22", "B22"]}],
    ),
    (
        "mix_of_pins_and_pinset",
        [
            {"name": "sys_clk", "pins": "G22"},
            {"name": "ref_clk", "pinset": {"p": "H22", "n": "H23"}},
        ],
    ),
]


@pytest.mark.parametrize(
    "signals",
    [pytest.param(s, id=n) for n, s in VALID_UNIQUE_PINS],
)
def test_valid_unique_pins(signals: list[dict]) -> None:
    """Check that signals with unique pins passes"""
    _check_unique_pins(signals)


INVALID_UNIQUE_PINS = [
    (
        "duplicate_scalar_pins",
        [{"name": "sys_clk", "pins": "G22"}, {"name": "sys_rst", "pins": "G22"}],
    ),
    (
        "duplicate_pin_in_array",
        [{"name": "sys_clk", "pins": "G22"}, {"name": "led", "pins": ["A22", "G22"]}],
    ),
    (
        "duplicate_pinset_p",
        [
            {"name": "ref_clk", "pinset": {"p": "H22", "n": "H23"}},
            {"name": "aux_clk", "pinset": {"p": "H22", "n": "J23"}},
        ],
    ),
    (
        "duplicate_pinset_n",
        [
            {"name": "ref_clk", "pinset": {"p": "H22", "n": "H23"}},
            {"name": "aux_clk", "pinset": {"p": "J22", "n": "H23"}},
        ],
    ),
    (
        "pin_shared_between_pins_and_pinset",
        [
            {"name": "sys_clk", "pins": "H22"},
            {"name": "ref_clk", "pinset": {"p": "H22", "n": "H23"}},
        ],
    ),
]


@pytest.mark.parametrize(
    "signals",
    [pytest.param(s, id=n) for n, s in INVALID_UNIQUE_PINS],
)
def test_invalid_unique_pins(signals: list[dict]) -> None:
    """Confirm that duplicate pins raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_unique_pins(signals)


# ---------------------------------------------------------------------------
# Semantic validation - _check_pinset_array_mismatch
# ---------------------------------------------------------------------------

VALID_PINSET_ARRAY_MISMATCH = [
    (
        "scalar_pinset",
        {"name": "ref_clk", "pinset": {"p": "H22", "n": "H23"}},
    ),
    (
        "array_pinset_same_length",
        {"name": "lvds_data", "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]}},
    ),
    (
        "no_pinset",
        {"name": "sys_clk", "pins": "G22"},
    ),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in VALID_PINSET_ARRAY_MISMATCH],
)
def test_valid_pinset_array_mismatch(sig: dict) -> None:
    """Check that consistent pinset types pass"""
    _check_pinset_array_mismatch(sig)


INVALID_PINSET_ARRAY_MISMATCH = [
    (
        "p_scalar_n_array",
        {"name": "ref_clk", "pinset": {"p": "H22", "n": ["H23"]}},
    ),
    (
        "p_array_n_scalar",
        {"name": "ref_clk", "pinset": {"p": ["H22"], "n": "H23"}},
    ),
    (
        "p_n_length_mismatch",
        {"name": "lvds_data", "pinset": {"p": ["AA1", "AB1"], "n": ["AA2"]}},
    ),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in INVALID_PINSET_ARRAY_MISMATCH],
)
def test_invalid_pinset_array_mismatch(sig: dict) -> None:
    """Confirm that mismatched pinset types raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_pinset_array_mismatch(sig)


# ---------------------------------------------------------------------------
# Semantic validation - _check_pins_array_width_match
# ---------------------------------------------------------------------------

VALID_PINS_ARRAY_WIDTH_MATCH = [
    (
        "width_matches_array",
        {"name": "led", "pins": ["A22", "B22", "C22", "D22"], "width": 4},
    ),
    (
        "scalar_pins_no_width",
        {"name": "sys_clk", "pins": "G22"},
    ),
    (
        "single_bit_array_pins_with_width",
        {"name": "sys_clk", "pins": ["G22"], "width": 1},
    ),
    (
        "generate_false_skipped",
        {"name": "reserved", "pins": ["X0", "X1"], "generate": False},
    ),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in VALID_PINS_ARRAY_WIDTH_MATCH],
)
def test_valid_pins_array_width_match(sig: dict) -> None:
    """Check that correct or skipped width declarations pass"""
    _check_pins_array_width_match(sig)


INVALID_PINS_ARRAY_WIDTH_MATCH = [
    (
        "width_too_large",
        {"name": "led", "pins": ["A22"], "width": 2},
    ),
    (
        "width_too_small",
        {"name": "led", "pins": ["A22", "B22"], "width": 1},
    ),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in INVALID_PINS_ARRAY_WIDTH_MATCH],
)
def test_invalid_pins_array_width_match(sig: dict) -> None:
    """Confirm that width mismatches raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_pins_array_width_match(sig)


# ---------------------------------------------------------------------------
# Semantic validation - _check_pinset_array_width_match
# ---------------------------------------------------------------------------

VALID_PINSET_ARRAY_WIDTH_MATCH = [
    (
        "width_matches_array",
        {"name": "lvds_data", "pinset": {"p": ["AA1", "AB1", "AC1"], "n": ["AA2", "AB2", "AC2"]}, "width": 3},
    ),
    (
        "scalar_pinset_no_width",
        {"name": "ref_clk", "pinset": {"p": "H22", "n": "H23"}},
    ),
    (
        "generate_false_skipped",
        {"name": "reserved", "pinset": {"p": ["H22", "H24"], "n": ["H23", "H25"]}, "generate": False},
    ),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in VALID_PINSET_ARRAY_WIDTH_MATCH],
)
def test_valid_pinset_array_width_match(sig: dict) -> None:
    """Check that correct or skipped pinset width declarations pass"""
    _check_pinset_array_width_match(sig)


INVALID_PINSET_ARRAY_WIDTH_MATCH = [
    (
        "width_too_large",
        {"name": "lvds_data", "pinset": {"p": ["AA1"], "n": ["AA2"]}, "width": 2},
    ),
    (
        "width_too_small",
        {"name": "lvds_data", "pinset": {"p": ["AA1", "AB1"], "n": ["AA2", "AB2"]}, "width": 1},
    ),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in INVALID_PINSET_ARRAY_WIDTH_MATCH],
)
def test_invalid_pinset_array_width_match(sig: dict) -> None:
    """Confirm that pinset width mismatches raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_pinset_array_width_match(sig)


# ---------------------------------------------------------------------------
# Semantic validation - _check_buffer_direction
# ---------------------------------------------------------------------------

VALID_BUFFER_DIRECTION = [
    ("ibuf_in",       {"name": "sig", "buffer": "ibuf",   "direction": "in"}),
    ("obuf_out",      {"name": "sig", "buffer": "obuf",   "direction": "out"}),
    ("ibufds_in",     {"name": "sig", "buffer": "ibufds", "direction": "in"}),
    ("obufds_out",    {"name": "sig", "buffer": "obufds", "direction": "out"}),
    ("iobuf_inout",   {"name": "sig", "buffer": "iobuf",  "direction": "inout"}),
    ("generate_false_skipped", {"name": "sig", "generate": False}),
    ("bypass_true_skipped",    {"name": "sig", "bypass": True, "direction": "out"}),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in VALID_BUFFER_DIRECTION],
)
def test_valid_buffer_direction(sig: dict) -> None:
    """Check that compatible buffer/direction pairs pass"""
    _check_buffer_direction(sig)


INVALID_BUFFER_DIRECTION = [
    ("ibuf_out",      {"name": "sig", "buffer": "ibuf",   "direction": "out"}),
    ("ibuf_inout",    {"name": "sig", "buffer": "ibuf",   "direction": "inout"}),
    ("obuf_in",       {"name": "sig", "buffer": "obuf",   "direction": "in"}),
    ("obuf_inout",    {"name": "sig", "buffer": "obuf",   "direction": "inout"}),
    ("ibufds_out",    {"name": "sig", "buffer": "ibufds", "direction": "out"}),
    ("ibufds_inout",  {"name": "sig", "buffer": "ibufds", "direction": "inout"}),
    ("obufds_in",     {"name": "sig", "buffer": "obufds", "direction": "in"}),
    ("obufds_inout",  {"name": "sig", "buffer": "obufds", "direction": "inout"}),
    ("iobuf_in",      {"name": "sig", "buffer": "iobuf",  "direction": "in"}),
    ("iobuf_out",     {"name": "sig", "buffer": "iobuf",  "direction": "out"}),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in INVALID_BUFFER_DIRECTION],
)
def test_invalid_buffer_direction(sig: dict) -> None:
    """Confirm that incompatible buffer/direction pairs raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_buffer_direction(sig)


# ---------------------------------------------------------------------------
# Semantic validation - _check_buffer_strategy_match
# ---------------------------------------------------------------------------

VALID_BUFFER_STRATEGY_MATCH = [
    ("ibuf_pins",    {"name": "sig", "buffer": "ibuf",   "pins": "G22"}),
    ("obuf_pins",    {"name": "sig", "buffer": "obuf",   "pins": "G22"}),
    ("iobuf_pins",   {"name": "sig", "buffer": "iobuf",  "pins": "G22"}),
    ("ibufds_pinset", {"name": "sig", "buffer": "ibufds", "pinset": {"p": "H22", "n": "H23"}}),
    ("obufds_pinset", {"name": "sig", "buffer": "obufds", "pinset": {"p": "H22", "n": "H23"}}),
    ("generate_false_skipped", {"name": "sig", "generate": False, "pins": "G22"}),
    ("bypass_true_skipped",    {"name": "sig", "bypass": True, "pins": "G22"}),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in VALID_BUFFER_STRATEGY_MATCH],
)
def test_valid_buffer_strategy_match(sig: dict) -> None:
    """Check that compatible buffer/pin strategy pairs pass"""
    _check_buffer_strategy_match(sig)


INVALID_BUFFER_STRATEGY_MATCH = [
    ("ibuf_pinset",   {"name": "sig", "buffer": "ibuf",   "pinset": {"p": "H22", "n": "H23"}}),
    ("obuf_pinset",   {"name": "sig", "buffer": "obuf",   "pinset": {"p": "H22", "n": "H23"}}),
    ("iobuf_pinset",  {"name": "sig", "buffer": "iobuf",  "pinset": {"p": "H22", "n": "H23"}}),
    ("ibufds_pins",   {"name": "sig", "buffer": "ibufds", "pins": "G22"}),
    ("obufds_pins",   {"name": "sig", "buffer": "obufds", "pins": "G22"}),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in INVALID_BUFFER_STRATEGY_MATCH],
)
def test_invalid_buffer_strategy_match(sig: dict) -> None:
    """Confirm that incompatible buffer/pin strategy pairs raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_buffer_strategy_match(sig)


# ---------------------------------------------------------------------------
# Semantic validation - _check_buffer_infer_bypass_mismatch
# ---------------------------------------------------------------------------

VALID_BUFFER_INFER_BYPASS_MISMATCH = [
    ("infer_only",  {"name": "sig", "infer": True,  "buffer": "ibuf"}),
    ("bypass_only", {"name": "sig", "bypass": True}),
    ("neither",     {"name": "sig", "buffer": "ibuf"}),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in VALID_BUFFER_INFER_BYPASS_MISMATCH],
)
def test_valid_buffer_infer_bypass_mismatch(sig: dict) -> None:
    """Check that signals with only one or neither of infer/bypass pass"""
    _check_buffer_infer_bypass_mismatch(sig)


INVALID_BUFFER_INFER_BYPASS_MISMATCH = [
    (
        "both_infer_and_bypass",
        {"name": "sig", "infer": True, "bypass": True},
    ),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in INVALID_BUFFER_INFER_BYPASS_MISMATCH],
)
def test_invalid_buffer_infer_bypass_mismatch(sig: dict) -> None:
    """Confirm that infer: true and bypass: true together raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_buffer_infer_bypass_mismatch(sig)


# ---------------------------------------------------------------------------
# Semantic validation - _check_buffer_inferable
# ---------------------------------------------------------------------------

VALID_BUFFER_INFERABLE = [
    ("ibuf_infer_true",      {"name": "sig", "buffer": "ibuf",   "infer": True}),
    ("obuf_infer_true",      {"name": "sig", "buffer": "obuf",   "infer": True}),
    ("infer_false",          {"name": "sig", "buffer": "ibufds", "infer": False}),
    ("infer_not_set",        {"name": "sig", "buffer": "ibufds"}),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in VALID_BUFFER_INFERABLE],
)
def test_valid_buffer_inferable(sig: dict) -> None:
    """Check that inferrable buffers or infer: false pass"""
    _check_buffer_inferable(sig)


INVALID_BUFFER_INFERABLE = [
    ("ibufds_infer_true", {"name": "sig", "buffer": "ibufds", "infer": True}),
    ("obufds_infer_true", {"name": "sig", "buffer": "obufds", "infer": True}),
    ("iobuf_infer_true",  {"name": "sig", "buffer": "iobuf",  "infer": True}),
]


@pytest.mark.parametrize(
    "sig",
    [pytest.param(s, id=n) for n, s in INVALID_BUFFER_INFERABLE],
)
def test_invalid_buffer_inferable(sig: dict) -> None:
    """Confirm that non-inferrable buffers with infer: true raise ValidationError"""
    with pytest.raises(ValidationError):
        _check_buffer_inferable(sig)


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
