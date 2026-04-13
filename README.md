# IO Gen

## Overview

A common task for FPGA design engineers is to define top level RTL port names,
IO buffer types, and XDC pin constraints during initial bring up of a new
hardware platform. This is typically a very manual and time-consuming process,
with errors and inconsistencies not being found until later in the design
process, when changing them can be problematic. The purpose of `io-gen` is to
automate the bulk of this process and allow the top level RTL, IO components
and initial XDC constraints to be derived from a single-source of truth. In
particular, it

- Allows all top level port names and IO buffers to be defined in a
  human-readable YAML file
- Creates a top level RTL module or entity with consistently named ports and an
  IO ring instantiated within that is responsible for all buffer instantiation.
  Bypassing the IO ring and buffer inference are both supported.
- Creates all signal declarations from the IO ring instantiation to user logic
- Creates an XDC file with all `IOSTANDARD` and `PACKAGE_PIN` constraints

The goals for the tool are the following:

- Top level port names should follow a predictable and simple pattern:
  single-ended signals denoted by `_pad` and differential signals denoted by
  `_p` and `_n`.
- Minimize the use of strings like `_o` and `_i` to indicate direction.
  Bidirectional buffers are an exception to this.
- Produce generally human-readable output, with the expectation that users will
  use an external tool to format their code (e.g., verible).

This is a one-shot code generation tool. The intent is that the YAML would be
written and checked against the schematic and vendor documentation by the
engineer, then `io-gen` would be run to generate the output files. At that
point, the output files would be committed to version control and owned by the
project as the design matured. The tool does not attempt to update or patch
existing files.

---

## Installation

`io-gen` requires Python 3.11 or later. To install from GitHub

```bash
pip install git+https://github.com/gmcastil/io-gen.git
```

or to install from a local clone use `pip`

```
pip install .
```

On macOS with `homebrew` installed, it's usually preferable to use `pipx` to
install the tool locally.

```
pipx install .
```

For development, an editable installation keeps the source files in place, so
changes will take effect immediately

```
pip install -e .
```

After installation, the `io-gen` command will be available in the PATH.

---

## Usage

```
io-gen --top NAME [--lang LANG] [--output DIR] [--validate-only | --rtl-only | --xdc-only] input.yaml
```

`--top NAME` is required. Sets the HDL module or entity name and drives all
output file names. Must be a valid HDL identifier.

`--lang verilog|vhdl` selects the output language (default: `verilog`). Ignored
when `--xdc-only` is specified.

`--output DIR` sets the output directory (default: current directory). Created
if it does not exist.

The following three options are mutually exclusive:

- `--validate-only` — parse and validate the input YAML without writing any
  output. Exits non-zero on failure. Useful in CI.
- `--rtl-only` — generate HDL files only. Skip the XDC file.
- `--xdc-only` — generate the XDC file only. Skip HDL files. `--lang` is not
  required.

### Example

```
io-gen --top example --lang verilog --output out/ examples/example.yaml
```

Produces `out/example.xdc`, `out/example.v`, and `out/example_io.v`. Reference
output for all supported signal types is in `examples/`.

---

## Examples

The `examples/` directory contains a reference YAML file covering every
supported signal type, along with the expected generated output files. The
`validation/` directory contains a YAML file describing the pins of the
Digilent Basys3 FPGA board and a `Makefile` which uses Vivado to run the IO
planning default DRC on the output XDC file. See
[examples/README.md](examples/README.md) for details.

---

## Developer Documentation

See [docs/README.md](docs/README.md) for internal design documentation covering
pipeline architecture, data structures, stage interfaces, and conventions.
