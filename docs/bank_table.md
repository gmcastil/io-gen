# Bank Table

## Overview

`BankTable` is a temporary data structure used only during signal table
construction to resolve IOSTANDARD inheritance. It is not passed to any
downstream stage.

`BankTable` is a plain dict mapping bank number (int) to a `Bank` dataclass
instance.

---

## Bank Dataclass

Each value in the `BankTable` dict is a `Bank` dataclass:

| Field         | Type | Source                            | Notes                  |
| ------------- | ---- | --------------------------------- | ---------------------- |
| `iostandard`  | str  | `yaml["banks"][N]["iostandard"]`  | Bank-level IO standard |
| `performance` | str  | `yaml["banks"][N]["performance"]` | HP, HR, or HD          |

The bank number `N` is the dict key and is not duplicated in the dataclass.

---

## Construction

```
BankTable(doc)
```

**Input:** the validated YAML document as a plain dict

**Output:** a `BankTable` instance (dict of int -> Bank)

Built directly from the top-level `banks` map in the YAML document. No
resolution or inheritance is required.

---

## Notes

- `BankTable` is discarded after `SignalTable` construction is complete.
- Signals with no `banks` map in the YAML are valid only if every signal
  carries its own `iostandard` override.
