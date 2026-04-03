# Signal Table

## Overview

`SignalTable` is the primary output of table construction. One row per signal,
fully resolved - no inheritance, no implicit values. Passed to all generation
stages.

---

## Fields

Each entry is a dict. The presence of `pins` or `pinset` distinguishes
single-ended from differential signals. Signals with `generate: false` in
the YAML are excluded from the table entirely and never reach generators.

### Single-ended

| Key          | Type             | Notes                                                                               |
| ------------ | ---------------- | ----------------------------------------------------------------------------------- |
| `name`       | str              |                                                                                     |
| `direction`  | str              | `in` / `out` / `inout`                                                              |
| `buffer`     | str or None      | None when `bypass: true`                                                            |
| `iostandard` | str              |                                                                                     |
| `width`      | int              | Always present - 1 for scalar, 1+ for bus                                           |
| `pins`       | str or list[str] | str = scalar, list = bus                                                            |
| `infer`      | bool             | Normalized to False if absent in YAML                                               |
| `bypass`     | bool             | Normalized to False if absent in YAML                                               |
| `comment`    | dict             | optional `xdc` and/or `hdl` string keys - empty dict if absent                      |
| `instance`   | str or None      | None when `bypass: true`; auto-generated as `<buffer_type>_<signal_name>` otherwise |

### Differential

| Key          | Type        | Notes                                                                               |
| ------------ | ----------- | ----------------------------------------------------------------------------------- |
| `name`       | str         |                                                                                     |
| `direction`  | str         | `in` / `out` / `inout`                                                              |
| `buffer`     | str or None | None when `bypass: true`                                                            |
| `iostandard` | str         |                                                                                     |
| `width`      | int         | Always present - 1 for scalar pair, 1+ for bus                                      |
| `pinset`     | dict        | `{'p': str or list[str], 'n': str or list[str]}`                                    |
| `infer`      | bool        | Normalized to False if absent in YAML                                               |
| `bypass`     | bool        | Normalized to False if absent in YAML                                               |
| `comment`    | dict        | optional `xdc` and/or `hdl` string keys - empty dict if absent                      |
| `instance`   | str or None | None when `bypass: true`; auto-generated as `<buffer_type>_<signal_name>` otherwise |

---

## Normalization

`add()` is responsible for applying all defaults. `build_signal_table()` calls
`add()` for each signal in the document. The `jsonschema` validator does not
inject default values - it only validates. Fields absent from the YAML will not
appear in the signal dict, so every default listed here must be applied
explicitly in `add()` using `sig.get(field, default)`.

| Field      | Default                                                 |
| ---------- | ------------------------------------------------------- |
| `infer`    | `False`                                                 |
| `bypass`   | `False`                                                 |
| `width`    | `1`                                                     |
| `comment`  | `{}`                                                    |
| `instance` | `<buffer_type>_<signal_name>` (None for `bypass: true`) |
| `buffer`   | `None`                                                  |

---

## Construction

```
build_signal_table(doc)
```

**Input:** the validated YAML document as a plain dict

**Output:** a `SignalTable` instance

---

## Notes

- Signals with `generate: false` in the YAML are excluded from the table
  entirely. Generators never see them and do not need to check for them.
- `comment` is always a dict. Use `sig["comment"].get("xdc")` to safely
  retrieve optional subfields.
- `is_bus` is not present in the signal table. It is derived during pin table
  construction from whether `pins` or `pinset.p` is a str or list.
- Used as input to `PinTable` construction.
