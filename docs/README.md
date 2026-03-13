# Developer Documentation

This folder contains internal design documentation for `io-gen`. It is intended
for developers working on the tool, not end users.

---

## Pipeline Architecture

The pipeline takes a validated YAML document through three stages in order:

```
YAML file
  -> 1. Validation (structural + semantic)
  -> 2. Table Construction (signal table + pin table + bank table + meta table)
  -> 3. Generation
        -> XDC constraints          (from pin table + signal table)
        -> HDL port declarations    (from signal table)
        -> HDL signal declarations  (from signal table)
        -> IO ring                  (from pin table + signal table)
```

After validation passes, all subsequent stages can trust their inputs
completely. No defensive checks are needed downstream.

---

## Error Handling Philosophy

- Validation is the only stage that handles user errors
- Validation raises on the first error encountered
- Stages after validation treat unexpected conditions as pipeline bugs,
  not user errors
- Generation stages do not validate their inputs

---

## Stage Documentation

- [Pipeline](pipeline.md)
- [Validation](validation.md)
- [Table Construction](table_construction.md)
- [Generation](generation.md)
- [CLI](cli.md)

---

## Data Structures

- [Meta Table](meta_table.md)
- [Signal Table](signal_table.md)
- [Pin Table](pin_table.md)

---

## Conventions

- [Output and Naming Conventions](conventions.md)
- [Schema Design Notes](schema.md)
- [Supported Buffer Types](buffers.md)

---

## Pending Work

- [Todo](todo.md)
