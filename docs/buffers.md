# Supported Buffer Types

The following buffer types are supported. The schema in `io_gen/schema/defs/buffer.json`
is the authoritative source - this file reflects it.

| Buffer   | Direction | Pin Strategy | Description                       |
| -------- | --------- | ------------ | --------------------------------- |
| `ibuf`   | `in`      | `pins`       | Single-ended input buffer         |
| `obuf`   | `out`     | `pins`       | Single-ended output buffer        |
| `iobuf`  | `inout`   | `pins`       | Single-ended bidirectional buffer |
| `ibufds` | `in`      | `pinset`     | Differential input buffer         |
| `obufds` | `out`     | `pinset`     | Differential output buffer        |

## Deferred

`iobufds` (differential bidirectional) is a valid use case but is intentionally
omitted until the base set above is working end-to-end.
