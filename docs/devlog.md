# Development Log

Entries are in reverse chronological order.

---

## 2026-04-09 - Addressing lingering validation items

- `validate_verilog` and `validate_vhdl` stubs added to validate.py
- \_check_non_ascii added to checks.py
- Enriched jsonschema error messages with signal name
- `_is_valid_verilog`\_identifier implemented in identifiers.py
- CLI and pipeline complete, first successful end-to-end run
- examples/example_io.v identified as stale
- The run_pipeline function was starting to do low level checks, which i've
  moved into language specific validate functions. Tests for these are needed.

## 2026-04-06 - Verilog generation is completed and CLI wired up

**Commit:** `7009b79` - "First time able to run the application"

- First successful run against a real YAML!
- I have a copy of the Arty Z7-20 YAML I had made and it erupted in errors
  because it's probably the wrong format
- Wired up the CLI to the pipeline `run_pipeline` function
- Updated the `pyproject.toml` file to use the appropriate build backend
- The examples are a little stale, so the next thing to do is make sure that the
  code is generating things in the way that I want and then use the generator to
  create the actual example stuff.
- Make sure that's all done and that the VHDL has the format we really want (now
  that I know what that is).

Deferred: Need to validate VHDL and Verilog identifiers

## 2026-04-04 - Verilog generation complete through buffer instantiation

**Commit:** `82672ff` - "Verilog IO buffer generation is working"

Completed the Verilog generation stage through buffer instantiation:

- `generate_verilog_top` and all private helpers implemented and tested
- `_generate_verilog_ioring_body` implemented using a dispatch table
  (`_INSTANTIATE_BUFFERS`, `_INFER_BUFFERS`) keyed by buffer type — adding
  a new buffer type requires one function and one dict entry
- Per-buffer instantiation functions for all five supported types: `ibuf`,
  `obuf`, `ibufds`, `obufds`, `iobuf` — scalar and bus cases both covered
- `infer: true` signals collapse to a single `assign` statement regardless
  of bus width — no pin table lookup needed
- `_indent_join` added to `formatting.py` and used throughout ioring generators
- Buffer instantiations use Xilinx port ordering (O first) and consistent
  4-char port name field alignment (`.{port:<3}(net)`)
- All buffer instances use `//#(` and `//)` header lines for future generics
- 256 tests passing

Remaining for Verilog: `_generate_verilog_ioring_ports` and
`generate_verilog_ioring` assembler.

Deferred: VHDL generators until Verilog is validated end-to-end in Vivado.
XDC validation will use Vivado I/O Planning project (UG899) rather than
full synthesis.

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
