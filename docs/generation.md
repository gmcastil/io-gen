# Generation

## Overview

Generation is the third pipeline stage. It consists of four independent
generators, each receiving only the table(s) it needs. Signals with
`generate: false` are skipped by all generators.

---

## Generators

### XDC Constraints

**Input:** pin table + signal table

Emits one `set_property PACKAGE_PIN` and one `set_property IOSTANDARD`
constraint per pin row. The signal table is used for grouping constraints
by signal and emitting signal-level comments for readability.

---

### HDL Port Declarations

**Input:** signal table

Emits one port declaration per signal. Bus signals use the `width` field.
Differential signals emit a port for each leg.

---

### HDL Signal Declarations

**Input:** signal table

Emits one internal signal declaration per signal. Same structure as port
declarations but for internal wires or signals.

---

### IO Ring

**Input:** pin table + signal table

Emits one buffer instantiation per pin row, connected to the corresponding
signal from the signal table. The signal table provides the port-side
connection names; the pin table provides the primitive-side pin assignments.
