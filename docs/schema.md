# Schema Design Notes

## Top-Level Fields

The root of the YAML has three required fields:

- `title` - a human-readable description of the design
- `part` - the FPGA part number
- `signals` - the list of signal descriptors

The optional `banks` map defines bank-level defaults for IOSTANDARD and
performance class. When provided, scalar signals (single pin or single
differential pair) that do not specify their own `iostandard` can inherit
it from their bank entry. Array signals must always specify `iostandard`
explicitly because a bus may span pins in different banks and there is no
single bank to inherit from. Multibank inheritance is not supported.

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

Beyond that, every signal must have `name`, `direction`, and `buffer` unless
`generate` is explicitly set to `false`, or `bypass` is set to `true`. When
`generate` is false, only `name` and a pin assignment strategy are required.
When `bypass` is true, `name` and `direction` are required but `buffer` is not.
This allows a signal to be declared in the YAML for documentation or reservation
purposes without producing any HDL output.

## Pin Assignment Strategies

Every signal must use exactly one of two pin assignment strategies:

- `pins` - single-ended, either a scalar string (one pin) or an array of
  strings (a bus). A scalar string means no bus indexing; an array means
  bus indexing applies even if only one element.
- `pinset` - differential pair, with `p` and `n` legs each being either a
  scalar string (one pair) or an array of strings (a bus of pairs). Same
  scalar vs array distinction applies.

## Width

`width` is required whenever `pins` or `pinset.p` is an array, regardless
of how many elements it contains. For scalar `pins` or `pinset`, width is
implicitly 1 and does not need to be declared.

## IOSTANDARD Inheritance

`iostandard` is resolved at signal scope. Scalar signals (one pin or one
differential pair) may inherit from a bank:

1. Signal-level `iostandard` override
2. Bank-level `iostandard` from the top-level `banks` map

Array signals (buses) must always specify `iostandard` explicitly. A bus may
span pins in different banks and there is no single bank to inherit from.
Inheritance from multiple banks is not supported. This is enforced by the
schema.

A scalar signal may specify both `bank` and `iostandard`. In that case the
signal-level value takes precedence and the bank default is ignored for that
signal. This is intentional - individual signals within a bank may use
different IOSTANDARDs provided they are compatible with the bank's VCCO
voltage. Compatibility checking is not enforced by the schema and is left to
a future validation pass or the downstream toolchain.

All pins in a signal share the same IOSTANDARD. Specifying different
IOSTANDARDs within a single logical bus would be incoherent electrically and
is not supported.

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
still receives a top-level port and XDC constraints. `buffer` is not required
when `bypass: true`.

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

Buffer instance names are auto-generated from the signal name and bit index
(e.g. `ibuf_sys_clk` for a scalar, `obuf_led_0` for a bus).
The optional `instance` field on a signal overrides the auto-generated name
for the entire signal. Per-pin instance name overrides are not supported.
