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
  -> 2. Table Construction (signal table + bank table)
  -> 3. Flattening (pin table)
  -> 4. Generation
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
table to resolve IOSTANDARD.

| Field        | Type    | Notes                                        |
| ------------ | ------- | -------------------------------------------- |
| name         | string  | signal name                                  |
| direction    | enum    | in, out, inout                               |
| buffer       | enum    | ibuf, obuf, ibufds, obufds, iobuf, infer     |
| width        | integer | always explicit, 1 for scalars               |
| iostandard   | string  | resolved from signal or bank, never implicit |
| differential | boolean | true for pinset signals                      |
| group        | string  | optional categorical label                   |
| instance     | string  | optional HDL instance name, nullable         |
| generate     | boolean | false signals are excluded from generation   |
| comment      | object  | optional xdc and hdl comment strings         |

The signal table has no knowledge of pin assignments or bank numbers.
It is used for HDL generation and for grouping and commenting XDC output.

### Pin Table

One row per pin (or per differential pair for pinset signals). Fully
resolved - no inheritance, no implicit values. Constructed from the
signal table and the original pin assignment data.

| Field       | Type    | Notes                                                |
| ----------- | ------- | ---------------------------------------------------- |
| signal_name | string  | reference to parent signal                           |
| index       | integer | bit position within the signal (0-based)             |
| pin_p       | string  | physical pin name (or positive leg for differential) |
| pin_n       | string  | negative leg for differential, null for single-ended |
| iostandard  | string  | resolved, copied from signal table                   |
| direction   | enum    | copied from signal table                             |
| buffer      | enum    | copied from signal table                             |

Rows are ordered by `signal_name` and then by `index`, so that buffer
instantiations for a bus are always sequential and grouped by signal.

The pin table has no knowledge of signal-level structure. It is used
for XDC generation and IO ring buffer instantiation.

### Bank Table

A temporary structure used only during table construction to resolve
IOSTANDARD inheritance. Not passed to any generation stage.

| Field       | Type    | Notes                  |
| ----------- | ------- | ---------------------- |
| bank        | integer | bank number            |
| iostandard  | string  | bank-level IO standard |
| performance | enum    | HP, HR, HD             |

---

## Stages

### 1. Validation

**Input:** a YAML file path

**Structural validation** checks that the YAML conforms to the JSON
schema. This catches missing required fields, invalid enum values,
wrong types, and constraint violations defined in the schema.

**Semantic validation** checks domain correctness that the schema cannot
express:

- All bank numbers referenced by signals exist in the banks map
- Multibank segment bank numbers are unique within a signal
- Multibank segment offsets are non-overlapping and collectively cover
  the full signal width
- pinset p and n arrays have equal length
- Buffer type is compatible with direction (e.g. ibuf requires in)

**Output on success:** the validated YAML document as a parsed object,
guaranteed to be structurally and semantically correct.

**Errors:** all validation errors are collected and reported together
rather than stopping at the first error. Each error includes the signal
name and field that caused it.

---

### 2. Table Construction

**Input:** the validated YAML document

Constructs the signal table and bank table from the validated YAML.
IOSTANDARD is resolved at this stage using the following precedence:

1. Signal-level iostandard override
2. Bank-level iostandard from the banks map

Signals with generate: false are included in the signal table but
flagged so that generation stages can skip them.

**Output:** signal table + bank table, both fully resolved.

**Errors:** none expected - the input is already validated. Any error
here is a pipeline bug.

---

### 3. Flattening

**Input:** signal table + bank table + original pin assignment data

Expands each signal into individual pin rows in the pin table:

- Scalar pins/pinset become a single row at index 0
- Array pins/pinset become one row per element
- Multibank signals are expanded using the offset field of each segment
  to place rows at the correct index positions

IOSTANDARD and all signal-level properties are copied into each row.
After flattening, the bank table is no longer needed.

**Output:** pin table, fully resolved and ordered by signal name and
index.

**Errors:** none expected - the input is already validated. Any error
here is a pipeline bug.

---

### 4. Generation

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
- All validation errors are collected and reported together, not one at a time
- Stages after validation treat unexpected conditions as pipeline bugs,
  not user errors
- Generation stages do not validate their inputs

---

## Todo

### Open design questions

None.

### Pending implementation

- [ ] Write the validator tool
- [ ] Define the signal table and pin table as concrete data structures
- [ ] Write tests for table construction
- [ ] Write tests for flattening
- [ ] Write tests for each generator

