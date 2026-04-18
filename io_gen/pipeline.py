from pathlib import Path

from io_gen.validate import validate, validate_verilog, validate_vhdl

from io_gen.tables import (
    build_signal_table,
    build_pin_table,
    build_meta_table,
    build_constraints_table,
)

from io_gen.generate import (
    generate_xdc,
    generate_verilog_top,
    generate_verilog_ioring,
    generate_vhdl_top,
    generate_vhdl_ioring,
)


def run_pipeline(
    yaml_path: str | Path,
    top: str,
    lang: str,
    output_dir: str | Path,
    validate_only: bool,
    rtl_only: bool,
    xdc_only: bool,
) -> None:
    """Run the full io-gen pipeline from YAML input to output files.

    Validates the input YAML, constructs tables, calls the appropriate
    generators based on the supplied flags, and writes output files to
    output_dir. Raises ValidationError on validation failure.

    Parameters
    ----------
    yaml_path:
        Path to the input YAML pin description file.
    top:
        HDL module name. Drives output file names and the IO ring module name.
    lang:
        Output HDL language: 'verilog' or 'vhdl'. Ignored when xdc_only is True.
    output_dir:
        Directory to write output files into.
    validate_only:
        If True, validate and return without generating any output.
    rtl_only:
        If True, generate HDL files only. Skip XDC.
    xdc_only:
        If True, generate XDC only. Skip HDL files.
    """

    # Convert to Path objects first
    output_dir = Path(output_dir).resolve()
    yaml_path = Path(yaml_path).resolve()

    # If the output directory doesn't exist already, make it (might raise
    # OSError which is being caught higher up)
    if not validate_only:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / ".io_gen_probe"
        # Now prove that it's writable (this will raise a PermissionError if not)
        probe.touch()
        # If the preceding raises an exception, then nothing will have been created
        # probe.unlink(missing_ok=True)
        probe.unlink()

    # Get the validated data from YAML
    valid_doc = validate(yaml_path)
    print(f"Info: Validated YAML at {yaml_path}")

    # Create the table of metadata
    meta_table = build_meta_table(valid_doc)

    # Create the table additional constraints to pass to the XDC generator
    constraints_table = build_constraints_table(valid_doc)

    # Create the table of signals from the validated doc
    signal_table = build_signal_table(valid_doc)
    # Now that we know the language and top level module or component names, we validate
    # the signal table components
    if lang == "verilog":
        validate_verilog(signal_table, top)
    else:
        validate_vhdl(signal_table, meta_table, top)

    # Create a mapping between signal names and a list of the pins for that signal
    pin_table = build_pin_table(signal_table)

    # If we're only validating the YAML, we're out of here now
    if validate_only:
        return

    if not rtl_only:
        with open(output_dir / f"{top}.xdc", "w", encoding="utf-8") as xdc:
            xdc.write(
                generate_xdc(
                    signal_table, pin_table, constraints_table, pin_planner=xdc_only
                )
            )
            print(f"Info: Wrote XDC constraints to {output_dir / f'{top}.xdc'}")

    if not xdc_only:
        if lang == "verilog":
            # Write the top level RTL to disk
            with open(output_dir / f"{top}.v", "w", encoding="utf-8") as top_rtl:
                top_rtl.write(generate_verilog_top(signal_table, top))
                print(f"Info: Wrote top level module to {output_dir / f'{top}.v'}")
            # Write the IO ring RTL to disk
            with open(output_dir / f"{top}_io.v", "w", encoding="utf-8") as top_rtl:
                top_rtl.write(generate_verilog_ioring(signal_table, pin_table, top))
                print(f"Info: Wrote IO ring module to {output_dir / f'{top}_io.v'}")
        else:
            # Write the top level RTL to disk
            with open(output_dir / f"{top}.vhd", "w", encoding="utf-8") as top_rtl:
                top_rtl.write(generate_vhdl_top(signal_table, meta_table, top))
                print(f"Info: Wrote top level module to {output_dir / f'{top}.vhd'}")
            # Write the IO ring RTL to disk
            with open(output_dir / f"{top}_io.vhd", "w", encoding="utf-8") as top_rtl:
                top_rtl.write(
                    generate_vhdl_ioring(signal_table, pin_table, meta_table, top)
                )
                print(f"Info: Wrote IO ring module to {output_dir / f'{top}_io.vhd'}")
