# Meta Table

## Overview

`MetaTable` is a simple dataclass containing the top-level descriptive fields from
the validated YAML document. It is constructed first, before any other table,
and is available for future stages that need design-level metadata.

---

## Fields

| Field   | Type | Source          | Notes                      |
| ------- | ---- | --------------- | -------------------------- |
| `title` | str  | `yaml["title"]` | Human-readable design name |
| `part`  | str  | `yaml["part"]`  | FPGA part number           |

---

## Construction

```
MetaTable(doc)
```

**Input:** the validated YAML document as a plain dict

**Output:** a `MetaTable` instance

No resolution or inheritance is required. Both fields are copied directly
from the top-level YAML document.

---

## Notes

- `MetaTable` is a flat dataclass.
