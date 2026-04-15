# Output Conventions

## Port Naming

### Top-Level Module

All top-level ports are pad-facing. The naming convention is:

- Single-ended: `<name>_pad`
- Differential positive leg: `<name>_p`
- Differential negative leg: `<name>_n`

This applies to every signal regardless of buffer type, including signals with
`infer: true` or `bypass: true`.

### IO Ring

The IO ring has both a pad-facing side and a fabric-facing side.

Pad-facing ports of the IO ring mirror the top-level port names exactly.

Fabric-facing ports use the bare signal name for unidirectional signals:

- Input or output: `<name>`

Tristate signals require three fabric-facing ports:

- `<name>_i` - value read from the pad (output from IO ring to fabric)
- `<name>_o` - value driven to the pad (input to IO ring from fabric)
- `<name>_t` - tristate enable, active high (output disabled when high)

The `_i`/`_o`/`_t` naming follows the perspective of the fabric, not the
primitive. Note that Xilinx IOBUF port `I` connects to `<name>_o`, and
IOBUF port `O` connects to `<name>_i`.

---

## XDC Constraints

Port names in `get_ports` calls must match the top-level HDL port names
exactly. This means:

- Single-ended ports: `<name>_pad`
- Differential ports: `<name>_p`, `<name>_n`

When referring to `IOSTANDARD` and `PACKAGE_PIN` in documentation they should
be capitalized and surrounded with back-ticks.

---

## Primitive Instance Naming

Buffer instance names always include a `_i<N>` index suffix, starting at 0.
There is no special case for scalars.

Auto-generated base name: `<buffer_type>_<signal_name>`

- Scalar: `<buffer_type>_<signal_name>_i0`
- Bus: `<buffer_type>_<signal_name>_i0`, `<buffer_type>_<signal_name>_i1`, ...

If the optional `instance` field is supplied on a signal, it overrides the
auto-generated base name. The `_i<N>` suffix is still appended by the generator.

- Scalar with override: `<instance>_i0`
- Bus with override: `<instance>_i0`, `<instance>_i1`, ...

Examples: `ibuf_sys_clk_i0`, `obuf_led_i0`, `obuf_led_i1`, `ibufds_serdes_rx_i3`

---

## Primitive Port Connections

Xilinx primitive port conventions used in the IO ring:

| Primitive | Ports                                                                        |
| --------- | ---------------------------------------------------------------------------- |
| IBUF      | I (pad in), O (fabric out)                                                   |
| OBUF      | I (fabric in), O (pad out)                                                   |
| IBUFDS    | I (pad p), IB (pad n), O (fabric out)                                        |
| OBUFDS    | I (fabric in), O (pad p), OB (pad n)                                         |
| IOBUF     | IO (pad), I (fabric \_o), O (fabric \_i), T (fabric \_t)                     |
| IOBUFDS   | IO (pad p), IOB (pad n), I (fabric \_o), O (fabric \_i), T (fabric \_t)     |

Both VHDL and Verilog use uppercase primitive names (IBUF, OBUF, IBUFDS, OBUFDS, IOBUF, IOBUFDS).
This matches the Xilinx UNISIM library source and documentation style. VHDL is case-insensitive
so lowercase would also compile, but uppercase is the convention.

---

## Infer and Bypass

When `infer: true` is specified, no primitive is instantiated. The IO ring
connects the pad-facing port directly to the fabric-facing port with a wire
(Verilog) or signal assignment (VHDL). The synthesis tool infers the
appropriate buffer from context.

When `bypass: true` is specified, the signal will not be included in the IO
ring, no internal signal will be created, and it will simply be dangling in the
HDL. It will still receive a port in the top level RTL and the corresponding
`IOSTANDARD`, `PACKAGE_PIN`, and `DIRECTION` constraints in the XDC.

---

## Output Files

The tool produces three output files per invocation. All file names are
derived from the `<top>` positional argument supplied at runtime. Files are written
to the directory specified by `--output`. Generation of HDL or XDC only is also
supported.

| File             | Contents                                  |
| ---------------- | ----------------------------------------- |
| `<top>.xdc`      | Pin assignment, IOSTANDARD, and DIRECTION constraints |
| `<top>.<ext>`    | Top-level module or entity with port list |
| `<top>_io.<ext>` | IO ring with buffer instantiations        |

Where `<ext>` is `v` for Verilog or `vhd` for VHDL, selected by `--lang`
at runtime.

The IO ring module or entity name matches the file stem: `<top>_io`.

---

## Formatting

Generated output is indented and readable by hand. For projects that
require consistent formatting, post-process the output with a dedicated
formatter:

- Verilog: `verible-verilog-format`
- VHDL: `vsg --fix`

The generator does not run these tools automatically. Formatting is left
to the user.
