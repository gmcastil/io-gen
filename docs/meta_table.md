# Meta

## Overview

`Meta` is a simple dataclass containing the top-level descriptive fields from
the validated YAML document. It is constructed first, before any other table,
and passed to any stage that needs design-level metadata.

---

## Fields

| Field   | Type | Source         | Notes                        |
| ------- | ---- | -------------- | ---------------------------- |
| `title` | str  | `yaml["title"]`| Human-readable design name   |
| `part`  | str  | `yaml["part"]` | FPGA part number             |

---

## Construction

```
Meta(doc)
```

**Input:** the validated YAML document as a plain dict

**Output:** a `Meta` instance

No resolution or inheritance is required. Both fields are copied directly
from the top-level YAML document.

---

## Notes

- `Meta` is not a table and does not wrap a list. It is a flat dataclass.
