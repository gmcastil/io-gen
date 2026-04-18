# Meta Table

## Overview

`MetaTable` is a simple dataclass containing the top-level descriptive fields from
the validated YAML document. It is constructed first, before any other table,
and is available for stages that need design-level metadata (e.g., the VHDL
architecture).

---

## Fields

| Field          | Type      | Source                   | Notes                                                                 |
| -------------- | --------- | ------------------------ | --------------------------------------------------------------------- |
| `title`        | str       | `yaml["title"]`          | Human-readable design name                                            |
| `part`         | str       | `yaml["part"]`           | FPGA part number                                                      |
| `architecture` | str\|None | `yaml["architecture"]`   | VHDL architecture name (e.g. `rtl`). None if not present in the YAML |

---

## Construction

```
build_meta_table(doc)
```

**Input:** the validated YAML document as a plain dict

**Output:** a `MetaTable` instance

No resolution or inheritance is required. All fields are copied directly
from the top-level YAML document. `architecture` defaults to `None` if absent.

---

## Notes

- `MetaTable` is a flat dataclass.
- `architecture` is required when generating VHDL. `validate_vhdl` raises
  `ValidationError` if it is `None` or not a valid VHDL identifier.
- Both VHDL generators (`generate_vhdl_top`, `generate_vhdl_ioring`) take
  `meta_table` as a parameter to access the architecture name.
