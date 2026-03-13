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

TBD - pip install instructions once packaged.

---

## Usage

TBD - basic invocation, flag descriptions, and a short example.

---

## Output Files

For a given `--top` name and `--lang` selection, `io-gen` produces up to three
files in the output directory:

| File             | Contents                                  |
| ---------------- | ----------------------------------------- |
| `<top>.xdc`      | Pin assignment and IOSTANDARD constraints |
| `<top>.<ext>`    | Top-level module or entity with port list |
| `<top>_io.<ext>` | IO ring with buffer instantiations        |

Where `<ext>` is `v` for Verilog or `vhd` for VHDL. Generation of HDL or XDC
only is also supported via `--rtl-only` and `--xdc-only`.

---

## Examples

The `examples/` directory contains a reference YAML file covering every
supported signal type, along with the expected generated output files. It also
describes an end-to-end hardware validation flow that runs the full chain from
YAML through Vivado to a bitstream on a Basys 3, providing concrete proof that
the tool produces correct, synthesizable output. See
[examples/README.md](examples/README.md) for details.

---

## Developer Documentation

See [docs/README.md](docs/README.md) for internal design documentation covering
pipeline architecture, data structures, stage interfaces, and conventions.
