from pathlib import Path
from textwrap import dedent

import pytest

from io_gen.exceptions import ValidationError
from io_gen.pipeline import run_pipeline


VALID_YAML = dedent("""\
    title: Pipeline Test Design
    part: xc7k325tffg900-2
    architecture: rtl
    constraints:
      cfgbvs: GND
      config_voltage: 1.8
    signals:
      - name: sys_clk
        pins: G22
        iostandard: LVCMOS18
        direction: in
        buffer: ibuf
""")

INVALID_YAML = dedent("""\
    title: Bad Design
    part: xc7k325tffg900-2
    constraints:
      cfgbvs: GND
      config_voltage: 1.8
    signals:
      - name: sys_clk
        pins: G22
        iostandard: LVCMOS18
        direction: in
""")


def write_yaml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "input.yaml"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# validate_only
# ---------------------------------------------------------------------------


def test_validate_only_no_files_written(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, VALID_YAML)
    out = tmp_path / "out"
    out.mkdir()
    run_pipeline(yaml_path, "top", "verilog", out, validate_only=True, rtl_only=False, xdc_only=False)
    assert list(out.iterdir()) == []


def test_validate_only_invalid_yaml_raises(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, INVALID_YAML)
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(ValidationError):
        run_pipeline(yaml_path, "top", "verilog", out, validate_only=True, rtl_only=False, xdc_only=False)


# ---------------------------------------------------------------------------
# Full run
# ---------------------------------------------------------------------------


def test_full_run_verilog_produces_expected_files(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, VALID_YAML)
    out = tmp_path / "out"
    run_pipeline(yaml_path, "top", "verilog", out, validate_only=False, rtl_only=False, xdc_only=False)
    assert (out / "top.xdc").exists()
    assert (out / "top.v").exists()
    assert (out / "top_io.v").exists()


def test_full_run_vhdl_produces_expected_files(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, VALID_YAML)
    out = tmp_path / "out"
    run_pipeline(yaml_path, "top", "vhdl", out, validate_only=False, rtl_only=False, xdc_only=False)
    assert (out / "top.xdc").exists()
    assert (out / "top.vhd").exists()
    assert (out / "top_io.vhd").exists()


# ---------------------------------------------------------------------------
# Flag behavior
# ---------------------------------------------------------------------------


def test_rtl_only_no_xdc(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, VALID_YAML)
    out = tmp_path / "out"
    run_pipeline(yaml_path, "top", "verilog", out, validate_only=False, rtl_only=True, xdc_only=False)
    assert (out / "top.v").exists()
    assert (out / "top_io.v").exists()
    assert not (out / "top.xdc").exists()


def test_xdc_only_no_rtl(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, VALID_YAML)
    out = tmp_path / "out"
    run_pipeline(yaml_path, "top", "verilog", out, validate_only=False, rtl_only=False, xdc_only=True)
    assert (out / "top.xdc").exists()
    assert not (out / "top.v").exists()
    assert not (out / "top_io.v").exists()


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------


def test_output_dir_created_if_missing(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, VALID_YAML)
    out = tmp_path / "does" / "not" / "exist"
    assert not out.exists()
    run_pipeline(yaml_path, "top", "verilog", out, validate_only=False, rtl_only=False, xdc_only=False)
    assert out.exists()


# ---------------------------------------------------------------------------
# Identifier validation
# ---------------------------------------------------------------------------


def test_invalid_top_identifier_raises(tmp_path: Path) -> None:
    yaml_path = write_yaml(tmp_path, VALID_YAML)
    out = tmp_path / "out"
    with pytest.raises(ValidationError):
        run_pipeline(yaml_path, "123bad", "verilog", out, validate_only=False, rtl_only=False, xdc_only=False)
