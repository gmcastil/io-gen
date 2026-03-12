# Table Construction

## Overview

Table construction is the second pipeline stage. It takes the validated YAML
document and produces a fully resolved signal table and pin table. The bank
table is a temporary intermediate used only within this stage.

---

## Interface

**Input:** the validated YAML document as a plain dict

**Output:** a `SignalTable` and a `PinTable`, both fully resolved

**Errors:** none expected - the input is already validated. Any error
here is a pipeline bug.

---

## Process

1. Build the `MetaTable` from the top-level YAML fields (see meta_table.md)
2. Build the `BankTable` from the top-level `banks` map (see bank_table.md)
3. Build the `SignalTable` from the signals list, resolving IOSTANDARD for
   scalar signals using the bank table (see signal_table.md)
4. Discard the bank table
5. Build the `PinTable` from the signal table (see pin_table.md)

---

## IOSTANDARD Resolution

Resolved at this stage for scalar signals only, using the following precedence:

1. Signal-level `iostandard` override
2. Bank-level `iostandard` from the bank table

Array signals always carry an explicit `iostandard` and require no resolution.

---

## Pin Table Flattening

Each signal row in the signal table is expanded into one or more pin rows:

- A scalar `pins` signal produces one `PinRow` with `is_bus: false`
- An array `pins` signal produces one `PinRow` per element with `is_bus: true`
- A scalar `pinset` signal produces one `PinSetRow` with `is_bus: false`
- An array `pinset` signal produces one `PinSetRow` per pair with `is_bus: true`

`is_bus` is derived from the type of the signal table `pins` or `pinset` field
(str vs list) and is not present in the YAML. Signals with `generate: false`
are excluded from the pin table.

---

## Notes

- Signals with `generate: false` are included in the signal table but flagged
  so that generation stages can skip them.
- The meta table is currently unused after construction.
- The bank table is discarded after the signal table is complete.
- The signal table is the primary data structure. The pin table is a lookup
  structure keyed by signal name, used by generators that need physical pin
  details.
