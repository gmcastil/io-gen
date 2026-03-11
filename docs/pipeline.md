# Pipeline

## Overview

The pipeline takes a YAML file describing FPGA IO assignments and produces:

- XDC constraint files (pin assignments and IO standards)
- HDL port declarations (VHDL or Verilog)
- HDL signal declarations
- IO ring code (buffer instantiations and connections)

The pipeline stages in order:

```
YAML file
  -> 1. Validation (structural + semantic)
  -> 2. Table Construction (signal table + pin table + bank table)
  -> 3. Generation
        -> XDC constraints          (from pin table + signal table)
        -> HDL port declarations    (from signal table)
        -> HDL signal declarations  (from signal table)
        -> IO ring                  (from pin table + signal table)
```

This is a one-shot generation tool. Output files are generated once,
committed to version control, and owned by the engineer from that point
forward. The tool does not update or patch existing files.

After validation passes, all subsequent stages can trust their inputs
completely. No defensive checks are needed downstream.

---

## Data Structures

- [Meta Table](meta_table.md)
- [Bank Table](bank_table.md)
- [Signal Table](signal_table.md)
- [Pin Table](pin_table.md)

---

## Stages

- [1. Validation](validation.md)
- [2. Table Construction](table_construction.md)
- [3. Generation](generation.md)

---

## Error Handling Philosophy

- Validation is the only stage that handles user errors
- Validation raises on the first error encountered
- Stages after validation treat unexpected conditions as pipeline bugs,
  not user errors
- Generation stages do not validate their inputs
