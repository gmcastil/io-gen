# Pipeline

## Overview

`pipeline.py` is the orchestrator. It drives all stages in order and
owns the handoff between them. It has no knowledge of how it was invoked - CLI,
test, or otherwise.

---

## Interface

```
run_pipeline(yaml_path, top, lang, output_dir, validate_only, rtl_only, xdc_only)
```

**Parameters:**

| Parameter       | Type | Notes                                           |
| --------------- | ---- | ----------------------------------------------- |
| `yaml_path`     | `str \| Path` | Path to the input YAML file                     |
| `top`           | `str`         | HDL module or entity name, drives output names  |
| `lang`          | `str`         | `verilog` or `vhdl`. Not required if XDC only   |
| `output_dir`    | `str \| Path` | Directory to write output files into            |
| `validate_only` | bool | Run validation only, no generation              |
| `rtl_only`      | bool | Generate HDL files only, skip XDC               |
| `xdc_only`      | bool | Generate XDC only, skip HDL files               |

**Returns:** nothing

**On failure:** propagates `ValidationError` from the validation stage.
The caller (CLI) is responsible for catching it and producing user-facing
output.

---

## Execution

1. Call validation with `yaml_path`. On failure, raise.
2. If `validate_only`, return.
3. Call table construction with the validated document.
4. Call the appropriate generators based on flags, collecting returned strings.
5. Write strings to files in `output_dir`.

---

## Generator Output Contract

Each generator returns a string. The pipeline is responsible for all file
I/O. Generators do not write files directly. This keeps generators testable
without file system involvement.

---

## Output Files

| Flag              | Files produced                               |
| ----------------- | -------------------------------------------- |
| (none)            | `<top>.xdc`, `<top>.<ext>`, `<top>_io.<ext>` |
| `--rtl-only`      | `<top>.<ext>`, `<top>_io.<ext>`              |
| `--xdc-only`      | `<top>.xdc`                                  |
| `--validate-only` | (none)                                       |
