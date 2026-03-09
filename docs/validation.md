# Validation

## Overview

Validation is the first pipeline stage. It takes a YAML file path as input.
On success it returns the parsed YAML document as a plain dict, guaranteed
to be structurally and semantically correct. On failure it returns a list of
error strings describing every problem found.

Validation has two passes that run in order:

1. **Structural validation** - checks that the document conforms to the JSON
   schema using `jsonschema` against `schema/schema.json`.

2. **Semantic validation** - checks domain correctness that the schema cannot
   express. Returns a list of error strings. An empty list means the document
   is semantically valid.

Structural validation runs first. If it fails, semantic validation does not
run - a structurally invalid document cannot be safely interpreted.

---

## Interface

**Input:** a YAML file path (string)

**Output on success:** the parsed YAML document as a plain dict

**Output on failure:** a non-empty list of error strings

Each error string identifies the signal name and the constraint that failed.
All errors from both passes are collected before returning - the caller
receives a complete picture of all problems.

---

## Structural Validation

Delegates to `jsonschema`. Catches missing required fields, wrong types,
invalid enum values, and schema-defined constraint violations.

---

## Semantic Validation

Checks that the document is meaningful and internally consistent. Signals
with `generate: false` are excluded.

The following constraints are enforced:

- All bank numbers referenced by signals exist in the top-level `banks` map
- `pinset.p` and `pinset.n` arrays have equal length
- Multibank segment bank numbers are unique within a signal
- Multibank segment offsets are non-overlapping and collectively cover the
  full signal width
- Mixing of `pins` and `pinset` across segments of the same `multibank`
  signal is not allowed
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

## Pending

- [ ] Define the exact error message format
- [ ] Decide whether structural and semantic errors go into the same list
      or are returned separately
- [ ] IOSTANDARD compatibility with bank VCCO voltage - deferred to a future
      validation pass or left to the downstream toolchain
