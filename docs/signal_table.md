# Signal Table

## Overview

`SignalTable` is the primary output of table construction. One row per signal,
fully resolved - no inheritance, no implicit values. Passed to all generation
stages.

---

## Fields

Each entry is a dict. The presence of `pins` or `pinset` distinguishes
single-ended from differential signals.

### Single-ended

| Key           | Type             | Notes                                    |
| ------------- | ---------------- | ---------------------------------------- |
| `name`        | str              |                                          |
| `direction`   | str              | `in` / `out` / `inout`                   |
| `buffer`      | str              | see buffer types in schema.md            |
| `iostandard`  | str              | fully resolved                           |
| `width`       | int              | 1 for scalar, 1+ for bus                 |
| `pins`        | str or list[str] | str = scalar, list = bus                 |
| `generate`    | bool             |                                          |
| `comment_xdc` | str or None      |                                          |
| `comment_hdl` | str or None      |                                          |
| `instance`    | str or None      | None = auto-generate                     |

### Differential

| Key           | Type             | Notes                                             |
| ------------- | ---------------- | ------------------------------------------------- |
| `name`        | str              |                                                   |
| `direction`   | str              | `in` / `out`                                      |
| `buffer`      | str              | see buffer types in schema.md                     |
| `iostandard`  | str              | fully resolved                                    |
| `width`       | int              | 1 for scalar pair, 1+ for bus                     |
| `pinset`      | dict             | `{'p': str or list[str], 'n': str or list[str]}`  |
| `generate`    | bool             |                                                   |
| `comment_xdc` | str or None      |                                                   |
| `comment_hdl` | str or None      |                                                   |
| `instance`    | str or None      | None = auto-generate                              |

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
