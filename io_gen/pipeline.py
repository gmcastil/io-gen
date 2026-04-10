import os
from pathlib import Path

from io_gen.validate import validate, validate_verilog, validate_vhdl
from io_gen.tables.signal_table import _build_signal_table
from io_gen.tables.pin_table import _build_pin_table
from io_gen.tables.meta_table import _build_meta_table

from io_gen.generate.xdc import generate_xdc
from io_gen.generate.verilog_top import generate_verilog_top
from io_gen.generate.verilog_ioring import generate_verilog_ioring


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

        # Before spinning anything up, lets make sure that the output
        # direcotry exists and is writable
        if not os.access(output_dir, os.W_OK):
            raise OSError(
                f"Output directory {output_dir} does not exist or is not writable by current user"
            )

    # Get the validated data from YAML
    valid_doc = validate(yaml_path)
    print(f"Info: Validated YAML at {yaml_path}")

    # Create the table of metadata
    meta_table = _build_meta_table(valid_doc)

    # Create the table of signals from the validated doc
    signal_table = _build_signal_table(valid_doc)
    # Now that we know the language and top level module or component names, we validate
    # the signal table components
    if lang == "verilog":
        validate_verilog(signal_table, top)
    else:
        validate_vhdl(signal_table, top)

    # Create a mapping between signal names and a list of the pins for that signal
    pin_table = _build_pin_table(signal_table)

    # If we're only validating the YAML, we're out of here now
    if validate_only:
        return None

    if not rtl_only:
        with open(output_dir / f"{top}.xdc", "w") as xdc:
            xdc.write(generate_xdc(signal_table, pin_table))
            print(f"Info: Wrote XDC constraints to {output_dir / f'{top}.xdc'}")

    if not xdc_only:
        if lang == "verilog":
            # Write the top level RTL to disk
            with open(output_dir / f"{top}.v", "w") as top_rtl:
                top_rtl.write(generate_verilog_top(signal_table, top))
                print(f"Info: Wrote top level module to {output_dir / f'{top}.v'}")
            # Write teh IO ring RTL to disk
            with open(output_dir / f"{top}_io.v", "w") as top_rtl:
                top_rtl.write(generate_verilog_ioring(signal_table, pin_table, top))
                print(f"Info: Wrote IO ring module to {output_dir / f'{top}_io.v'}")
        else:
            raise NotImplementedError(f"VHDL support not supported yet")

    return
