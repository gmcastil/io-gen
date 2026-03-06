# Pin Table Overview

The `pin_table` is the canonical, flattened represenetation of all physical I/O connections that will be emitted in HDL and XDC constraints.  Each entry in the pin table corresponds to an atomic unit, either:
- A single-ended pin or
- A differential pinset (a `p` and `n` pair)

The pin table is the final stage of processing before emission and only
contains signals that will actually be generated (i.e., all `generate: false`
entries in the board level YAML file will be filtered out).

The purpose of the pin table is to provide a uniform, fully-resolved view of
all pins on the board, independent of how they were described in the board
level YAML.  In particular, all multibank signal descriptions and bank
IOSTANDARD inheritance are resolved.  Every entry in the pin table contains an
index, a width if the pin or pinset is a member of an array, and a boolean
`bus` that indicates whether the pin is a bus or not. This removes the
ambiguity in how single-bit signals are to be handled. These allow all
downstream emission logic to operate without needing to branch on signal type
or inheritance logic.

## Structure
Each row in the pin table is one physical or differential port. Rows share a
common set of core fields and some variant ones, depending on their type.

### Common Fields

| Field        | Type                       | Description                                                        |
| ------------ | -------------------------- | ------------------------------------------------------------------ |
| `signal`     | string                     | Logical signal name (e.g., `led`)                           |
| `index`      | integer                    | Bus bit index (0 for scalars)                                      |
| `direction`  | `"in"`, `"out"`, `"inout"` | HDL port direction                                                 |
| `buffer`     | string                     | Buffer type (`ibuf`, `obuf`, `ibufds`, `obufds`, `iobuf`, `infer`) |
| `width`      | integer                    | Logical bus width of the parent signal                             |
| `bus`        | boolean                    | Indicates whether to emit as a bus (`foo[0]`) or scalar (`foo`)    |
| `iostandard` | string                     | Fully-resolved IO standard                                         |
| `group`      | string (optional)          | Logical grouping or subsystem tag                                  |
| `comment`    | object (optional)          | Contains free-form comments for `hdl` and/or `xdc` emitters        |
| `attrs`      | object (optional)          | Future per-pin attributes such as drive, slew, or pull-up          |

### Variant Fields

| Field  | Type    | Description            |
| ------ | ------- | ---------------------- |
| `pin`  | string  | FPGA package ball name |


| Field    | Type    | Description              |
| -------- | ------- | ------------------------ |
| `p`      | string  | Positive pin name        |
| `n`      | string  | Negative pin name        |

## Emission semantics

### HDL

### XDC
