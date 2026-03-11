# CLI Reference

## Usage

```
io-gen [options] <input.yaml> <top>
```

`<input.yaml>` is the path to the YAML pin description file.

`<top>` is the HDL module or entity name. Must be a valid HDL identifier.
Drives all output file names and the IO ring module or entity name (`<top>_io`).

## Options

### `--lang <vhdl|verilog>`

The output HDL language. Defaults to TBD. Not required when `--xdc-only`
is specified.

### `--output <dir>`

Directory to write output files into. Defaults to the current directory.

### `--validate-only`

Parse and validate the input YAML without generating any output. Exits with
a non-zero status code if validation fails, zero if it passes.

### `--rtl-only`

Generate only the HDL files (`<top>.<ext>` and `<top>_io.<ext>`). Skip
the XDC file.

### `--xdc-only`

Generate only the XDC file (`<top>.xdc`). Skip the HDL files. `--lang`
is not required when this flag is set.
