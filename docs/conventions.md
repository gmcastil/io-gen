# Output Conventions

## Port Naming

### Top-Level Module

All top-level ports are pad-facing. The naming convention is:

- Single-ended: `<name>_pad`
- Differential positive leg: `<name>_p`
- Differential negative leg: `<name>_n`

This applies to every signal regardless of buffer type. A signal with
`buffer: infer` still uses `_pad` or `_p`/`_n` at the top-level port.

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

---

## Primitive Instance Naming

Buffer instance names are auto-generated as:

- Scalar: `<buffer_type>_<signal_name>`
- Bus: `<buffer_type>_<signal_name>_<index>`

Examples: `ibuf_sys_clk`, `obuf_led_0`, `ibufds_serdes_rx_3`

---

## Primitive Port Connections

Xilinx primitive port conventions used in the IO ring:

| Primitive | Ports                                      |
| --------- | ------------------------------------------ |
| IBUF      | I (pad in), O (fabric out)                 |
| OBUF      | I (fabric in), O (pad out)                 |
| IBUFDS    | I (pad p), IB (pad n), O (fabric out)      |
| OBUFDS    | I (fabric in), O (pad p), OB (pad n)       |
| IOBUF     | IO (pad), I (fabric _o), O (fabric _i), T (fabric _t) |

Both VHDL and Verilog use uppercase primitive names (IBUF, OBUF, IBUFDS, OBUFDS, IOBUF).
This matches the Xilinx UNISIM library source and documentation style. VHDL is case-insensitive
so lowercase would also compile, but uppercase is the convention.

---

## Infer Buffer

When `buffer: infer` is specified, no primitive is instantiated. The IO
ring connects the pad-facing port directly to the fabric-facing port with
a wire (Verilog) or signal assignment (VHDL). The synthesis tool infers
the appropriate buffer from context.

---

## Formatting

Generated output is indented and readable by hand. For projects that
require consistent formatting, post-process the output with a dedicated
formatter:

- Verilog: `verible-verilog-format`
- VHDL: `vsg --fix`

The generator does not run these tools automatically. Formatting is left
to the user.
