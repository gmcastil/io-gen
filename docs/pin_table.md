# Pin Table

## Overview

`PinTable` is a lookup structure keyed by signal name. It is constructed by
flattening the signal table into individual pin rows during table construction.
It is not iterated independently - generators iterate the signal table and look
up pin details by signal name when needed.

---

## Structure

```
PinTable: dict[str, list[PinRow | PinSetRow]]
```

The key is the signal name. The value is an ordered list of `PinRow` or
`PinSetRow` dataclass instances, one per pin or differential pair. Position
in the list corresponds to bus index.

A signal's list contains either all `PinRow` or all `PinSetRow` instances -
never mixed.

---

## PinRow (single-ended)

| Field        | Type        | Notes                                  |
| ------------ | ----------- | -------------------------------------- |
| `pin`        | str         | Package pin name                       |
| `iostandard` | str         | Fully resolved                         |
| `direction`  | str         | `in` / `out` / `inout`                 |
| `buffer`     | str or None | None when `bypass: true`               |
| `infer`      | bool        |                                        |
| `instance`   | str         | Fully resolved: `<stem>_i<N>`          |
| `is_bus`     | bool        | True if signal uses array `pins`       |

---

## PinSetRow (differential)

| Field        | Type        | Notes                                  |
| ------------ | ----------- | -------------------------------------- |
| `pinset`     | dict        | `{'p': str, 'n': str}`                 |
| `iostandard` | str         | Fully resolved                         |
| `direction`  | str         | `in` / `out` / `inout`                 |
| `buffer`     | str or None | None when `bypass: true`               |
| `infer`      | bool        |                                        |
| `instance`   | str         | Fully resolved: `<stem>_i<N>`          |
| `is_bus`     | bool        | True if signal uses array `pinset`     |

---

## Construction

```
PinTable(signal_table)
```

**Input:** a `SignalTable` instance

**Output:** a `PinTable` instance

See table_construction.md for details of the flattening process.

---

## Notes

- Signals with `generate: false` are excluded.
- Signals with `bypass: true` are included - they still need XDC constraints.
- Generators iterate the signal table and look up entries in the pin table by
  signal name. The pin table is never iterated independently.
