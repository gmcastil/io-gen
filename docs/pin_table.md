# Pin Table

## Overview

`PinTable` is a lookup structure keyed by signal name. It is constructed by
flattening the signal table into individual pin rows during table construction.
It is not iterated independently - generators iterate the signal table and look
up pin details by signal name when needed.

---

## Structure

```
PinTable: dict[str, list[dict]]
```

The key is the signal name. The value is a list of dicts, one per pin or
differential pair. Each row carries its own `index` field.

A signal's list contains either all single-ended rows (with a `pin` key) or
all differential rows (with a `pinset` key) - never mixed.

---

## Single-ended row

| Field        | Type        | Notes                                                                     |
| ------------ | ----------- | ------------------------------------------------------------------------- |
| `pin`        | str         | Package pin name                                                          |
| `iostandard` | str         | Fully resolved                                                            |
| `direction`  | str         | `in` / `out` / `inout`                                                    |
| `buffer`     | str or None | None when `bypass: true`                                                  |
| `infer`      | bool        |                                                                           |
| `instance`   | str or None | Fully resolved: `<stem>_i<N>`; None when `bypass: true` or `infer: true` |
| `is_bus`     | bool        | True if signal uses array `pins`                                          |
| `index`      | int         | Position in the bus, 0-based; 0 for scalar signals                        |

---

## Differential row

| Field        | Type        | Notes                                                                     |
| ------------ | ----------- | ------------------------------------------------------------------------- |
| `pinset`     | dict        | `{'p': str, 'n': str}`                                                    |
| `iostandard` | str         | Fully resolved                                                            |
| `direction`  | str         | `in` / `out` / `inout`                                                    |
| `buffer`     | str or None | None when `bypass: true`                                                  |
| `infer`      | bool        |                                                                           |
| `instance`   | str or None | Fully resolved: `<stem>_i<N>`; None when `bypass: true` or `infer: true` |
| `is_bus`     | bool        | True if signal uses array `pinset`                                        |
| `index`      | int         | Position in the bus, 0-based; 0 for scalar signals                        |

---

## Construction

```
build_pin_table(signal_table: SignalTable) -> PinTable
```

**Input:** a `SignalTable` instance

**Output:** a `PinTable` instance

Iterates the signal table and calls `PinTable.add(sig_row)` for each row.
All rows in the signal table are included - `generate: false` signals are
filtered out during signal table construction and never appear here.

---

## PinTable.__getitem__()

```
__getitem__(name: str) -> list[dict]
```

Returns the list of pin rows for the given signal name. Raises `KeyError` if
the signal is not present. This is the primary retrieval interface -
generators use `pt[sig["name"]]` to look up rows. Internal access via
`pt.table[name]` is not part of the public interface.

---

## PinTable.add()

```
add(sig_row: dict) -> None
```

Calls `_flatten_signal(sig_row)` and stores the resulting list under
`sig_row["name"]` in the internal dict.

---

## _flatten_signal()

```
_flatten_signal(sig: dict) -> list[dict]
```

Module-level private function. Takes a single normalized signal table row
and returns a list of dicts, one per pin or differential pair.

Responsibilities:
- Derives `is_bus` from whether `pins` or `pinset["p"]` is a `list`
- Expands scalar or array `pins` into one row per pin
- Expands scalar or array `pinset` into one row per pair, pairing `pinset["p"][i]`
  with `pinset["n"][i]` to produce `{"p": ..., "n": ...}` per row
- Copies `iostandard`, `direction`, and `infer` from the signal row into every pin row unchanged
- Sets `index` to the bus position (0-based); scalars always get 0. Array
  order is index-preserving: `pins[0]` → `index=0`, `pins[1]` → `index=1`,
  etc. Same applies to `pinset["p"]` and `pinset["n"]`.
- Appends `_i<N>` to the signal table `instance` base name to produce
  the fully-resolved instance name for each row
- For `bypass: true` signals, `instance` is `None` and `buffer` is `None`
- For `infer: true` signals, `instance` is `None` but `buffer` is preserved

---

## Notes

- Signals with `generate: false` are excluded.
- Signals with `bypass: true` are included - they still need XDC constraints.
- Generators iterate the signal table and look up entries in the pin table by
  signal name. The pin table is never iterated independently.
