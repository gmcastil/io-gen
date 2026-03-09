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

1. Build the `BankTable` from the top-level `banks` map (see bank_table.md)
2. Build the `SignalTable` from the signals list, resolving IOSTANDARD for
   scalar signals using the bank table (see signal_table.md)
3. Discard the bank table
4. Build the `PinTable` from the signal table (see pin_table.md)

---

## IOSTANDARD Resolution

Resolved at this stage for scalar signals only, using the following precedence:

1. Signal-level `iostandard` override
2. Bank-level `iostandard` from the bank table

Array signals always carry an explicit `iostandard` and require no resolution.

---

## Notes

- Signals with `generate: false` are included in the signal table but flagged
  so that generation stages can skip them.
- The bank table is discarded after the signal table is complete.
- The signal table is used to construct the pin table.
