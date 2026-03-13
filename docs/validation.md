# Validation

## Overview

Validation is the first pipeline stage. It takes a YAML file path as input.
On success, it returns the parsed YAML document as a plain dict, guaranteed
to be structurally and semantically correct. On failure, it raises a
`ValidationError` exception containing a message describing the problem.

Validation has two passes that run in order:

1. **Structural validation** - checks that the document conforms to the JSON
   schema using `jsonschema` against `io_gen/schema/schema.json`.

2. **Semantic validation** - checks domain correctness that the schema cannot
   express.

Structural validation runs first. If it fails, semantic validation does not
run - a structurally invalid document cannot be safely interpreted.

---

## Interface

**Input:** a YAML file path (string)

**Output on success:** the parsed YAML document as a plain dict

**On failure:** raises `ValidationError` with a message identifying the
signal and constraint that failed. Raises on the first error encountered.

---

## Structural Validation

Delegates to `jsonschema`. Catches missing required fields, wrong types,
invalid enum values, and schema-defined constraint violations.

---

## Semantic Validation

Checks that the document is meaningful and internally consistent.

The following constraints are enforced:

- Signal names are unique across all signals defined in the YAML (this applies
  to signals with `generate: false` as well)
- Every pin name (in `pins` and both legs of `pinset`) must match the pattern
  `^[A-Z0-9]+$` - uppercase letters and digits only. Lowercase letters,
  whitespace, commas, brackets, and any other characters are rejected. Applies
  to all signals, including those with `generate: false`.
- Pin names are unique across all signals (no two signals may reference the
  same physical pin, including signals with `generate: false` as well)
- `pinset.p` and `pinset.n` must be the same type (both scalar or both array)
  and if arrays, must have equal length
- Pin arrays and `width` must match
- Pinset arrays and `width` must match
- Buffer type is compatible with direction (see [buffers.md](buffers.md)):
  - `ibuf` requires `in`
  - `obuf` requires `out`
  - `ibufds` requires `in`
  - `obufds` requires `out`
  - `iobuf` requires `inout`
- Buffer type is compatible with pin strategy (see [buffers.md](buffers.md)):
  - `ibuf`, `obuf`, `iobuf` require `pins`
  - `ibufds`, `obufds` require `pinset`
- `width` must equal the number of elements in `pins` or `pinset.p`
- `infer: true` and `bypass: true` are mutually exclusive
- If `bypass: true` then `buffer` cannot be provided
- When `infer: true`, the buffer type must be `ibuf` or `obuf`. These are the
  only types where synthesis inference is predictable and guaranteed correct.
  All other buffer types must be instantiated explicitly.

---

## Validate-Only Mode

The CLI supports a `--validate-only` flag that runs validation and reports
the result without proceeding to any generation stage. Exits with a non-zero
status code if validation fails. Useful for checking a YAML file in CI or
before a generation run.

---
