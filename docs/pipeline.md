# Pipeline

## Overview

The pipeline takes a YAML file describing FPGA IO assignments and produces:

- XDC constraint files (pin assignments and IO standards)
- HDL port declarations (VHDL or Verilog)
- HDL signal declarations
- IO ring code (buffer instantiations and connections)

The pipeline stages in order:

```
YAML file
  -> 1. Validation (structural + semantic)
  -> 2. Table Construction (signal table + pin table + bank table)
  -> 3. Generation
        -> XDC constraints          (from pin table + signal table)
        -> HDL port declarations    (from signal table)
        -> HDL signal declarations  (from signal table)
        -> IO ring                  (from pin table + signal table)
```

This is a one-shot generation tool. Output files are generated once,
committed to version control, and owned by the engineer from that point
forward. The tool does not update or patch existing files.

After validation passes, all subsequent stages can trust their inputs
completely. No defensive checks are needed downstream.

---

## Data Structures

### Signal Table

One row per signal. All properties are fully resolved - no inheritance,
no implicit values. Constructed from the validated YAML using the bank
table to resolve IOSTANDARD for scalar signals.

See `docs/signal_table.md` for the concrete dataclass definition.

### Pin Table

One row per pin (or per differential pair for pinset signals). Fully
resolved - no inheritance, no implicit values. Constructed from the
signal table during table construction.

See `docs/pin_table.md` for the concrete dataclass definition.

### Bank Table

A temporary structure used only during table construction to resolve
IOSTANDARD inheritance for scalar signals. Not passed to any generation
stage.

| Field       | Type    | Notes                  |
| ----------- | ------- | ---------------------- |
| bank        | integer | bank number            |
| iostandard  | string  | bank-level IO standard |
| performance | enum    | HP, HR, HD             |

---

## Stages

### 1. Validation

See `docs/validation.md`.

---

### 2. Table Construction

**Input:** the validated YAML document

Constructs the signal table, pin table, and bank table from the validated
YAML. IOSTANDARD is resolved at this stage for scalar signals using the
following precedence:

1. Signal-level iostandard override
2. Bank-level iostandard from the banks map

Array signals always carry an explicit iostandard and require no resolution.

The bank table is discarded after the signal table is complete. The signal
table is used to construct the pin table.

Signals with generate: false are included in the signal table but flagged
so that generation stages can skip them.

**Output:** signal table + pin table, both fully resolved.

**Errors:** none expected - the input is already validated. Any error
here is a pipeline bug.

---

### 3. Generation

Each generator is independent and receives only the table(s) it needs.
Signals with generate: false are skipped by all generators.

#### XDC Constraints

**Input:** pin table + signal table

Emits one set_property PACKAGE_PIN and one set_property IOSTANDARD
constraint per pin row. The signal table is used for grouping constraints
by signal and emitting signal-level comments for readability.

#### HDL Port Declarations

**Input:** signal table

Emits one port declaration per signal. Bus signals use the width field.
Differential signals emit a port for each leg.

#### HDL Signal Declarations

**Input:** signal table

Emits one internal signal declaration per signal. Same structure as
port declarations but for internal wires/signals.

#### IO Ring

**Input:** pin table + signal table

Emits one buffer instantiation per pin row, connected to the
corresponding signal from the signal table. The signal table provides
the port-side connection names; the pin table provides the primitive-
side pin assignments.

---

## Error Handling Philosophy

- Validation is the only stage that handles user errors
- Validation raises on the first error encountered
- Stages after validation treat unexpected conditions as pipeline bugs,
  not user errors
- Generation stages do not validate their inputs

---

## Todo

### Open design questions

- [ ] Define the signal table dataclass (see signal_table.md - pending)
- [ ] Define the pin table dataclass (see pin_table.md - pending)

### Pending implementation

- [ ] Write the validator tool
- [ ] Write tests for table construction
- [ ] Write tests for each generator
