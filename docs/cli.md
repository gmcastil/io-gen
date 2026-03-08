# CLI Reference

## Usage

```
io-gen [options] <input.yaml>
```

## Options

### `--top <name>`

The HDL module or entity name. Must be a valid HDL identifier. Drives all
output file names and the IO ring module or entity name (`<top>_io`).

### `--lang <vhdl|verilog>`

The output HDL language. Required unless `--xdc-only` is specified.

### `--output <dir>`

Directory to write output files into. If omitted, output is written to
stdout. See stdout mode below.

### `--rtl-only`

Generate only the HDL files (`<top>.<ext>` and `<top>_io.<ext>`). Skip
the XDC file.

### `--xdc-only`

Generate only the XDC file (`<top>.xdc`). Skip the HDL files. `--lang`
is not required when this flag is set.

## Stdout Mode

When `--output` is omitted, output is written to stdout instead of files.
Stdout mode is most useful with `--rtl-only` or `--xdc-only`, which
produce a single logical output. When generating all three files without
`--output`, the outputs are concatenated in the following order: XDC,
top-level HDL, IO ring HDL.

## Planned Features

- [ ] Stdout mode
- [ ] `--rtl-only` flag
- [ ] `--xdc-only` flag
