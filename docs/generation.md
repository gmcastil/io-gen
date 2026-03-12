# Generation

## Overview

Generation is the third pipeline stage. It consists of four independent
generators, each receiving only the table(s) it needs. Signals with
`generate: false` are skipped by all generators.

---

## Generators

### XDC Constraints

**Input:** signal table + pin table

Iterates the signal table. For each signal, emits any signal-level comment,
then looks up the signal's pin rows in the pin table and emits one
`set_property PACKAGE_PIN` and one `set_property IOSTANDARD` constraint
per pin row.

---

### HDL Port Declarations

**Input:** signal table

Emits one port declaration per signal. Bus signals use the `width` field.
Differential signals emit a port for each leg.

---

### HDL Signal Declarations

**Input:** signal table

Emits one internal signal declaration per signal. Same structure as port
declarations but for internal wires or signals. Signals with `bypass: true`
are excluded.

---

### IO Ring

**Input:** signal table + pin table

Iterates the signal table. For each signal, looks up the signal's pin rows
in the pin table and emits one buffer instantiation per pin row. The signal
table provides the port-side connection names; the pin table provides the
primitive-side pin assignments. Signals with `bypass: true` are excluded.
