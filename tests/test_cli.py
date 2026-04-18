import sys
from unittest.mock import patch

import pytest

from io_gen.cli import main
from io_gen.exceptions import ValidationError


# ---------------------------------------------------------------------------
# Argument forwarding
# ---------------------------------------------------------------------------


def test_args_forwarded_correctly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", [
        "io-gen", "--top", "mydesign", "--lang", "vhdl", "--output", "/tmp/out", "input.yaml"
    ])
    with patch("io_gen.cli.run_pipeline") as mock_run:
        main()
    mock_run.assert_called_once_with(
        yaml_path="input.yaml",
        top="mydesign",
        lang="vhdl",
        output_dir="/tmp/out",
        validate_only=False,
        rtl_only=False,
        xdc_only=False,
    )


def test_default_lang_is_verilog(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["io-gen", "--top", "top", "input.yaml"])
    with patch("io_gen.cli.run_pipeline") as mock_run:
        main()
    assert mock_run.call_args.kwargs["lang"] == "verilog"


def test_default_output_is_dot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["io-gen", "--top", "top", "input.yaml"])
    with patch("io_gen.cli.run_pipeline") as mock_run:
        main()
    assert mock_run.call_args.kwargs["output_dir"] == "."


# ---------------------------------------------------------------------------
# Mutual exclusion
# ---------------------------------------------------------------------------


def test_mutual_exclusion_validate_only_and_rtl_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", [
        "io-gen", "--top", "top", "--validate-only", "--rtl-only", "input.yaml"
    ])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2


def test_mutual_exclusion_validate_only_and_xdc_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", [
        "io-gen", "--top", "top", "--validate-only", "--xdc-only", "input.yaml"
    ])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_validation_error_exits_1(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    monkeypatch.setattr(sys, "argv", ["io-gen", "--top", "top", "input.yaml"])
    with patch("io_gen.cli.run_pipeline", side_effect=ValidationError("bad signal")):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
    assert "bad signal" in capsys.readouterr().err


def test_permission_error_exits_1(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    monkeypatch.setattr(sys, "argv", ["io-gen", "--top", "top", "input.yaml"])
    err = PermissionError(13, "Permission denied", "/some/path")
    with patch("io_gen.cli.run_pipeline", side_effect=err):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
    assert "Permission denied" in capsys.readouterr().err