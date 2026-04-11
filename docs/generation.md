# Generation

## Overview

Generation is the third pipeline stage. It consists of two top-level generator
functions per language, each responsible for one output file. Signals with
`generate: false` are excluded at signal table construction time and never
reach any generator.

---

## Module Layout

```
io_gen/generate/
    xdc.py              # generate_xdc
    verilog_top.py      # generate_verilog_top + private helpers
    verilog_ioring.py   # generate_verilog_ioring + private helpers
    vhdl_top.py         # generate_vhdl_top + private helpers
    vhdl_ioring.py      # generate_vhdl_ioring + private helpers
    common.py           # language-agnostic per-signal port/net helpers
    formatting.py       # indent_join, indent_strings
```

---

## Output Files

| File             | Public function           | Module                | Contents                           |
| ---------------- | ------------------------- | --------------------- | ---------------------------------- |
| `<top>.xdc`      | `generate_xdc`            | `xdc.py`              | Pin and IOSTANDARD constraints     |
| `<top>.<ext>`    | `generate_<lang>_top`     | `<lang>_top.py`       | Top-level module or entity         |
| `<top>_io.<ext>` | `generate_<lang>_ioring`  | `<lang>_ioring.py`    | IO ring with buffer instantiations |

Where `<ext>` is `v` or `vhd` and `<lang>` is `verilog` or `vhdl`.

---

## XDC Constraints

**Function:** `generate_xdc(signal_table, pin_table) -> str`

**Input:** signal table + pin table

Iterates the signal table. For each signal, emits any signal-level comment,
then looks up the signal's pin rows in the pin table and emits one
`set_property PACKAGE_PIN` and one `set_property IOSTANDARD` constraint
per pin row.

---

## HDL Top-Level File

**Public functions:**
- `generate_verilog_top(signal_table, top) -> str`
- `generate_vhdl_top(signal_table, meta_table, top) -> str`

**Input:** signal table (and meta table for VHDL, which carries the architecture name)

Assembles the complete top-level module or entity by calling private helpers
in order:

- `_generate_<lang>_ports(signal_table)` - pad-facing port declarations
- `_generate_<lang>_wires(signal_table)` - internal wire or signal declarations
- `_generate_<lang>_ioring_inst(signal_table)` - IO ring component instantiation

### _generate_<lang>_ports

Emits one port declaration per signal using pad-facing names: `<name>_pad`
(SE), `<name>_p` / `<name>_n` (diff). Bus signals use the `width` field.
An optional `comment.hdl` string is emitted as a comment line before each
signal's port(s). No blank lines between port groups. Commas follow every
declaration except the last.

### _generate_<lang>_wires

Emits one internal wire or signal declaration per signal. Signals with
`bypass: true` are excluded. Tristate signals (`iobuf`) emit three
declarations: `<name>_i`, `<name>_o`, `<name>_t`.

### _generate_<lang>_ioring_inst

Emits the instantiation of the IO ring component inside the top-level
module or architecture, connecting pad-facing ports and internal wires or
signals to the IO ring's corresponding ports.

---

## HDL IO Ring File

**Public functions:**
- `generate_verilog_ioring(signal_table, pin_table, top) -> str`
- `generate_vhdl_ioring(signal_table, pin_table, meta_table, top) -> str`

**Input:** signal table + pin table (and meta table for VHDL)

Assembles the complete IO ring module or entity by calling private helpers:

- `_generate_<lang>_ioring_ports(signal_table)` - IO ring port declarations,
  both pad-facing and fabric-facing
- `_generate_<lang>_ioring_body(signal_table, pin_table)` - buffer
  instantiations

### _generate_<lang>_ioring_ports

Emits pad-facing ports (same names as the top-level) and fabric-facing ports.
Fabric-facing naming:

- Unidirectional: `<name>` (bare signal name)
- Tristate: `<name>_i`, `<name>_o`, `<name>_t`

Signals with `bypass: true` are excluded entirely - they do not appear in
the IO ring at all. No blank lines between port groups.

### _generate_<lang>_ioring_body

Iterates the signal table. For each signal, looks up the signal's pin rows
in the pin table and emits one buffer instantiation per row using the fully
resolved instance name from the pin table. Signals with `bypass: true` or
`infer: true` are excluded. No comments are emitted.
