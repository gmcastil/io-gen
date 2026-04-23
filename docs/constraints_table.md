# Constraints Table

## Overview

The `ConstraintsTable` is a simple dataclass that holds the board-level Xilinx
device configuration properties extracted from the `constraints` block in the
YAML. These values are required by the Vivado XDC pin planner and must appear
in every generated XDC file.

---

## Interface

**Class:** `io_gen.tables.ConstraintsTable`

**Fields:**

| Field            | Type    | Valid Values              |
| ---------------- | ------- | ------------------------- |
| `cfgbvs`         | `str`   | `"VCCO"`, `"GND"`         |
| `config_voltage` | `float` | `1.5`, `1.8`, `2.5`, `3.3` |

**Factory:** `build_constraints_table(doc: dict) -> ConstraintsTable`

Extracts `cfgbvs` and `config_voltage` from `doc["constraints"]`. The input is
already validated, so no defensive checks are needed here.

---

## Why It Exists

Vivado's XDC pin planner requires `set_property CFGBVS` and
`set_property CONFIG_VOLTAGE` to be present in the XDC or it will reject the
constraints file. These values describe the power supply configuration of the
FPGA configuration bank and must match the actual board hardware.

See UG912 for full details on valid combinations.

---

## Usage

`ConstraintsTable` is built during table construction and passed directly to
`generate_xdc()`, which emits:

```
set_property CONFIG_VOLTAGE <config_voltage> [current_design]
set_property CFGBVS <cfgbvs> [current_design]
```

It is not used by HDL generators.

---

## Notes

- `cfgbvs = "VCCO"` is appropriate for 2.5V or 3.3V configuration banks
- `cfgbvs = "GND"` is appropriate for 1.5V or 1.8V configuration banks
- The valid combinations of `cfgbvs` and `config_voltage` differ between
  7-series and UltraScale/UltraScale+ devices. The schema currently enforces
  only the legal voltage values; cross-field consistency checking may be added
  in the future if device family support is extended.