# Development Log

Entries are in reverse chronological order.

---

## 2026-04-03 - Drop `generate` from signal table rows

**Commit:** `c4b7964` - "Massive refactor - removing `generate: false` from rows in SignalTable"

`generate: false` signals are now filtered out at signal table construction
time in `SignalTable.add()`. If the incoming signal dict has `generate` set
to `False` (or falsy), `add()` returns early and the signal is never appended
to the table.

As a result:

- Signal table rows no longer carry a `generate` key. Every row in the table
  is implicitly a generate-true signal.
- The pin table inherits this - `build_pin_table()` iterates the signal table
  directly with no additional filtering needed.
- Generators never see `generate: false` signals and must not check for a
  `generate` key in rows.
- `generate: false` remains a valid YAML-level field. It is recognized during
  semantic validation (`_check_minimum_ports_generated`) and consumed by
  `SignalTable.add()`. It does not survive into any table or generator.
