# Schema Design Notes

## Top-Level Fields

The root of the YAML has five required fields and one optional field:

- `title` - a human-readable description of the design
- `part` - the FPGA part number
- `CONFIG_VOLTAGE` - the configuration voltage for the FPGA, in volts. Must be
  one of `1.5`, `1.8`, `2.5`, or `3.3`. Sets the `CONFIG_VOLTAGE` property in
  the generated XDC. This must match the actual board supply voltage on the
  configuration bank or configuration failures and marginal I/O behavior can
  result. See UG912 for details.
- `CFGBVS` - the voltage selection signal for the configuration bank. Must be
  `VCCO` (for 3.3V or 2.5V operation) or `GND` (for 1.8V or 1.5V operation).
  Sets the `CFGBVS` property in the generated XDC. Must be consistent with
  `config_voltage`. See UG912 for details.
- `signals` - the list of signal descriptors
- `architecture` *(optional)* - the VHDL architecture name (e.g., `rtl`). Required
  when generating VHDL output; ignored for Verilog. Not enforced by the schema but
  validated at generation time by `validate_vhdl`.

## Signals

A signal is a named logical IO that maps to one or more physical FPGA pins.
It has a direction, a buffer type that gets instantiated in the IO ring, and
produces entries in the port list, XDC constraints, and IO ring code. A
signal consists of one of the following:

- A single pin or differential pair (scalar `pins` or `pinset`)
- A bus of pins or differential pairs (array `pins` or `pinset`)

## Signal Generation

Every signal must include a pin assignment strategy (`pins` or `pinset`)
regardless of whether `generate` is true or false. This ensures that every
signal in the file corresponds to a real physical pin assignment.

Beyond that, every signal must have `name`, `direction`, `buffer`, and
`iostandard` unless `generate` is explicitly set to `false`, or `bypass` is set
to `true`. When `generate` is false, only `name` and a pin assignment strategy
are required. This allows a signal to be declared in the YAML for documentation
or reservation purposes without producing any HDL or XDC output. When `bypass` is
true, `name`, `direction`, and `iostandard` must be provided. Additionally, if
`bypass` is true, `buffer` cannot be provided. This allows top level HDL ports
to be connected to internal components that provide their own buffer instances
(e.g., IP containing SERDES instances).

## Pin Assignment Strategies

Every signal must use exactly one of two pin assignment strategies:

- `pins` - single-ended, either a scalar string (one pin) or an array of
  strings (a bus). A scalar string means no bus indexing; an array means
  bus indexing applies even if only one element. Array order is
  index-preserving: `pins[0]` maps to `foo[0]`, `pins[1]` to `foo[1]`,
  and so on.
- `pinset` - differential pair, with `p` and `n` legs each being either a
  scalar string (one pair) or an array of strings (a bus of pairs). Same
  scalar vs array distinction applies.

## Width

`width` is required whenever `pins` or `pinset.p` is an array, regardless
of how many elements it contains. For scalar `pins` or `pinset`, width is
implicitly 1 and does not need to be declared.

## IOSTANDARD

Every signal except `generate: false` must carry an explicit `iostandard`.
There is no inheritance or bank-level default. All pins in a signal share the
same `iostandard`.

## Buffer Types

All pins in a signal share the same buffer type. `buffer` is a signal-level
property. There is an implicit relationship between buffer type and pin
strategy: single-ended buffers (`ibuf`, `obuf`, `iobuf`) go with `pins`, and
differential buffers (`ibufds`, `obufds`) go with `pinset`. See
[buffers.md](buffers.md) for the full list of supported buffer types.

## Infer

`infer` is an optional boolean (default `false`). When `true`, no primitive is
instantiated - the IO ring connects the pad-facing port directly to the
fabric-facing signal and synthesis infers the buffer. Only `ibuf` and `obuf`
are permitted when `infer: true` - these are the only types where inference
is predictable and guaranteed correct. `buffer` is still required when
`infer: true`.

## Bypass

`bypass` is an optional boolean (default `false`). When `true`, the signal is
excluded from the IO ring entirely and no internal signal is created. The signal
still receives a top-level port and XDC constraints. If `bypass: true` then `buffer`
must be omitted.

`infer: true` and `bypass: true` are mutually exclusive. Setting both is a
validation error.

## Comments

The optional `comment` field on a signal carries human-readable annotations
that are emitted in the generated output. It has two optional sub-fields:

- `xdc` - comment emitted in the XDC file above the signal's constraints
- `hdl` - comment emitted in the HDL files above the signal's port and
  signal declarations

Either or both sub-fields may be present. If `comment` is omitted entirely,
no comment is emitted for that signal.

---

## Instance Names

Buffer instance names are auto-generated as `<buffer_type>_<signal_name>_i<N>`,
where `N` starts at 0. There is no special case for scalars - they always get
`_i0`. The optional `instance` field on a signal overrides the auto-generated
base name; the `_i<N>` suffix is still appended by the generator. Per-pin
instance name overrides are not supported.
