# Pin Table

## Overview

`PinTable` is constructed from the signal table during table construction.
One row per pin, or per differential pair for pinset signals. Fully resolved -
no inheritance, no implicit values. Passed to the XDC and IO ring generators.

---

## Fields

TBD

---

## Construction

```
PinTable(signal_table)
```

**Input:** a `SignalTable` instance

**Output:** a `PinTable` instance

---

## Notes

- Constructed from the signal table after it is complete.
- Signals with `generate: false` are excluded.
