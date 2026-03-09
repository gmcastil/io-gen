# Signal Table

## Overview

`SignalTable` is the primary output of table construction. One row per signal,
fully resolved - no inheritance, no implicit values. Passed to all generation
stages.

---

## Fields

TBD

---

## Construction

```
SignalTable(doc, bank_table)
```

**Input:** the validated YAML document as a plain dict and a `BankTable`
instance

**Output:** a `SignalTable` instance

---

## Notes

- Signals with `generate: false` are included but flagged so generation
  stages can skip them.
- IOSTANDARD is resolved at this stage for scalar signals using the bank
  table. Array signals carry an explicit `iostandard` and require no
  resolution.
- Used as input to `PinTable` construction.
