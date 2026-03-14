# Signal Table

## Overview

`SignalTable` is the primary output of table construction. One row per signal,
fully resolved - no inheritance, no implicit values. Passed to all generation
stages.

---

## Fields

Each entry is a dict. The presence of `pins` or `pinset` distinguishes
single-ended from differential signals.

Signals with `generate: false` have a reduced row shape - see below.

### Single-ended (generate: true)

| Key          | Type             | Notes                                          |
| ------------ | ---------------- | ---------------------------------------------- |
| `name`       | str              |                                                |
| `direction`  | str              | `in` / `out` / `inout`                         |
| `buffer`     | str or None      | None when `bypass: true`                       |
| `iostandard` | str              |                                                |
| `width`      | int              | Always present - 1 for scalar, 1+ for bus      |
| `pins`       | str or list[str] | str = scalar, list = bus                       |
| `generate`   | bool             | Always True for this row shape                 |
| `infer`      | bool             | Normalized to False if absent in YAML          |
| `bypass`     | bool             | Normalized to False if absent in YAML          |
| `comment`    | dict             | optional `xdc` and/or `hdl` string keys - empty dict if absent |
| `instance`   | str              | Auto-generated as `<buffer_type>_<signal_name>` if absent in YAML |

### Differential (generate: true)

| Key          | Type        | Notes                                              |
| ------------ | ----------- | -------------------------------------------------- |
| `name`       | str         |                                                    |
| `direction`  | str         | `in` / `out` / `inout`                             |
| `buffer`     | str or None | None when `bypass: true`                           |
| `iostandard` | str         |                                                    |
| `width`      | int         | Always present - 1 for scalar pair, 1+ for bus     |
| `pinset`     | dict        | `{'p': str or list[str], 'n': str or list[str]}`   |
| `generate`   | bool        | Always True for this row shape                     |
| `infer`      | bool        | Normalized to False if absent in YAML              |
| `bypass`     | bool        | Normalized to False if absent in YAML              |
| `comment`    | dict        | optional `xdc` and/or `hdl` string keys - empty dict if absent |
| `instance`   | str         | Auto-generated as `<buffer_type>_<signal_name>` if absent in YAML |

### generate: false

| Key        | Type             | Notes                                     |
| ---------- | ---------------- | ----------------------------------------- |
| `name`     | str              |                                           |
| `pins`     | str or list[str] | present for single-ended signals          |
| `pinset`   | dict             | present for differential signals          |
| `width`    | int              | Always present - 1 for scalar, 1+ for bus |
| `generate` | bool             | Always False for this row shape           |

No other keys are present. Generation stages check `generate` first and skip
these rows entirely.

---

## Normalization

Table construction fills in the following defaults for `generate: true` signals
when the corresponding field is absent from the YAML:

| Field      | Default |
| ---------- | ------- |
| `infer`    | False   |
| `bypass`   | False   |
| `width`    | 1       |
| `comment`  | `{}`    |
| `instance` | `<buffer_type>_<signal_name>` |
| `buffer`   | None    |

For `generate: false` signals, only `width` is normalized (to 1 for scalar
pins or pinset).

---

## Construction

```
SignalTable(doc)
```

**Input:** the validated YAML document as a plain dict

**Output:** a `SignalTable` instance

---

## Notes

- Signals with `generate: false` are included but have a reduced row shape.
  Generation stages check `generate` first and skip these rows entirely.
- `comment` is always a dict. Use `sig["comment"].get("xdc")` to safely
  retrieve optional subfields.
- `is_bus` is not present in the signal table. It is derived during pin table
  construction from whether `pins` or `pinset.p` is a str or list.
- Used as input to `PinTable` construction.
