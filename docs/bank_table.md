# Bank Table

## Overview

`BankTable` is a temporary data structure used only during signal table
construction to resolve IOSTANDARD inheritance. It is not passed to any
downstream stage.

---

## Fields

Each entry in the bank table is a `Bank` dataclass:

| Field         | Type | Source                      | Notes                    |
| ------------- | ---- | --------------------------- | ------------------------ |
| `number`      | int  | key of `yaml["banks"]`      | Bank number              |
| `iostandard`  | str  | `yaml["banks"][n]["iostandard"]`  | Bank-level IO standard   |
| `performance` | str  | `yaml["banks"][n]["performance"]` | HP, HR, or HD            |

---

## Construction

```
BankTable(doc)
```

**Input:** the validated YAML document as a plain dict

**Output:** a `BankTable` instance

Built directly from the top-level `banks` map in the YAML document. No
resolution or inheritance is required.

---

## Notes

- `BankTable` is discarded after `SignalTable` construction is complete.
- Signals with no `banks` map in the YAML are valid only if every signal
  carries its own `iostandard` override.
