# Validation

## Overview

Validation is the first pipeline stage. It takes a YAML file path as input.
On success it returns the parsed YAML document as a plain dict, guaranteed
to be structurally and semantically correct. On failure it raises a
`ValidationError` exception containing a message describing the problem.

Validation has two passes that run in order:

1. **Structural validation** - checks that the document conforms to the JSON
   schema using `jsonschema` against `schema/schema.json`.

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

The parsed YAML dict must have its banks keys converted to strings before
passing to `jsonschema`, but the original dict (with integer keys) will be used
to construct the signal and bank tables.

---

## Semantic Validation

Checks that the document is meaningful and internally consistent. Signals
with `generate: false` are excluded.

The following constraints are enforced:

- All bank numbers referenced by signals exist in the top-level `banks` map
- If no `banks` map is present, every signal must carry its own `iostandard`
- Scalar signals with no signal-level `iostandard` must reference a `bank`
  that exists in the `banks` map and carries an `iostandard`
- `pinset.p` and `pinset.n` must be the same type (both scalar or both array)
  and if arrays, must have equal length
- Buffer type is compatible with direction:
  - `ibuf` requires `in`
  - `obuf` requires `out`
  - `ibufds` requires `in`
  - `obufds` requires `out`
  - `iobuf` requires `inout`
  - `infer` is compatible with any direction

---

## Validate-Only Mode

The CLI supports a `--validate-only` flag that runs validation and reports
the result without proceeding to any generation stage. Exits with a non-zero
status code if validation fails. Useful for checking a YAML file in CI or
before a generation run.

---
