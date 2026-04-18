import argparse
import sys

from io_gen.exceptions import ValidationError

from io_gen.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="io-gen",
        description="Generate XDC constraints and HDL from a YAML pin description.",
    )

    parser.add_argument(
        "--top",
        required=True,
        metavar="NAME",
        help="HDL module name. Drives all output file names and the IO ring name (<top>_io).",
    )
    parser.add_argument(
        "--lang",
        type=str.lower,
        choices=["verilog", "vhdl"],
        default="verilog",
        metavar="LANG",
        help="Output HDL language: verilog or vhdl (default: verilog). Ignored with --xdc-only.",
    )
    parser.add_argument(
        "--output",
        default=".",
        metavar="DIR",
        help="Directory to write output files into (default: current directory).",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the input YAML and exit. No output is generated.",
    )
    mode.add_argument(
        "--rtl-only",
        action="store_true",
        help="Generate HDL files only. Skip the XDC file.",
    )
    mode.add_argument(
        "--xdc-only",
        action="store_true",
        default=False,
        help="Generate XDC constraints only for an IO Planning project",
    )

    parser.add_argument(
        "input_yaml",
        metavar="input.yaml",
        help="Path to the YAML pin description file.",
    )

    args = parser.parse_args()

    try:
        run_pipeline(
            yaml_path=args.input_yaml,
            top=args.top,
            lang=args.lang,
            output_dir=args.output,
            validate_only=args.validate_only,
            rtl_only=args.rtl_only,
            xdc_only=args.xdc_only,
        )
    except PermissionError as e:
        print(f"Error: {e.strerror}: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except (ValidationError, OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
