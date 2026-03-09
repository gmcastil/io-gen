# Schema Design Notes

## Top-Level Fields

The root of the YAML has four required fields:

- `title` - a human-readable description of the design
- `part` - the FPGA part number
- `signals` - the list of signal descriptors

The optional `banks` map defines bank-level defaults for IOSTANDARD and
performance class.

## Signals

A signal is a named logical IO that maps to one or more physical FPGA pins.
It has a direction, a buffer type that gets instantiated in the IO ring, and
produces entries in the port list, XDC constraints, and IO ring code. A
signal consists of one of the following:

- A single pin or differential pair (scalar `pins` or `pinset`)
- A bus of pins or differential pairs within one bank (array `pins` or `pinset`)
- A bus of pins or differential pairs spread across more than one bank (`multibank`)

## Signal Generation

Every signal must have `name`, `direction`, and `buffer` unless `generate`
is explicitly set to `false`. When `generate` is false, only `name` is
required. This allows a signal to be declared in the YAML for documentation
or reservation purposes without producing any HDL output.

## Pin Assignment Strategies

Every signal must use exactly one of three pin assignment strategies:

- `pins` - single-ended, either a scalar string (one pin) or an array of
  strings (a bus). Arrays must have more than one item - a single-element
  array is disallowed; use a scalar string instead.
- `pinset` - differential pair, with `p` and `n` legs each being either a
  scalar string (one pair) or an array of strings (a bus of pairs). Arrays
  must have more than one item for the same reason as above.
- `multibank` - a bus whose pins are physically spread across multiple IO
  banks. Each segment identifies the bank, the pins or pinset within that
  bank, and an offset into the overall bus. A multibank signal must have at
  least two segments. Mixing `pins` and `pinset` across segments of the same
  signal is not allowed - the whole signal is either single-ended or
  differential.

## Width

`width` is required whenever a signal has more than one bit - that is,
whenever `pins` or `pinset.p` is an array, or whenever `multibank` is used.
For scalar `pins` or `pinset`, width is implicitly 1 and does not need to be
declared.

The reason `width` is required for `multibank` even when a segment has only
one pin is that it is valid for a bank to contribute a single pin to the
overall bus. Without an explicit `width` on the signal, the tool would be unable
to determine the total bit count from segment structure alone.

## IOSTANDARD Inheritance

`iostandard` is resolved at signal scope. The lookup order is:

1. Signal-level `iostandard` override
2. Bank-level `iostandard` from the top-level `banks` map

A signal may specify both `bank` and `iostandard`. In that case the
signal-level value takes precedence and the bank default is ignored for
that signal. This is intentional — individual signals within a bank may
use different IOSTANDARDs provided they are compatible with the bank's
VCCO voltage. Compatibility checking is not enforced by the schema and
is left to a future validation pass or the downstream toolchain.

All pins in a signal share the same IOSTANDARD. Specifying different
IOSTANDARDs within a single logical bus would be incoherent electrically and
is not supported. For `multibank` signals, `iostandard` belongs at the signal
level only.

## Buffer Types

All pins in a signal share the same buffer type. `buffer` is a signal-level
property. There is an implicit relationship between buffer type and pin
strategy: single-ended buffers (`ibuf`, `obuf`, `iobuf`) go with `pins`, and
differential buffers (`ibufds`, `obufds`) go with `pinset`. Since mixing
`pins` and `pinset` within a `multibank` signal is disallowed, the buffer
type constraint follows naturally.

## Bank and IOSTANDARD on Multibank Signals

The signal-level `bank` field exists to support IOSTANDARD inheritance for
`pins` and `pinset` signals. It is not meaningful for `multibank` signals
because each segment already carries its own `bank` reference. The signal-
level `bank` field should not be used on a `multibank` signal and is
rejected by the schema if present.

## Instance Names

Buffer instance names are auto-generated from the signal name and bit index
(e.g. `ibuf_sys_clk` for a scalar, `obuf_led_0` for a bus).
The optional `instance` field on a signal overrides the auto-generated name
for the entire signal. Per-pin instance name overrides are not supported.

