# Todo

## Design

- [x] Define the signal table dataclass fields (see signal_table.md)
- [x] Define the pin table dataclass fields (see pin_table.md)

## Implementation

### Validation

- [x] Write exhaustive unit tests for the buffer/direction compatibility checking logic
- [x] Write exhaustive unit tests for the buffer/pin strategy compatibility checking logic
- [x] Write the validator

### Table Construction

- [x] Write tests for MetaTable
- [x] Implement MetaTable and build_meta_table()
- [x] Write tests for SignalTable
- [x] Implement SignalTable and build_signal_table()
- [x] Write tests for PinTable
- [x] Implement PinTable and build_pin_table()
- [x] Add PinTable.__getitem__ (missing retrieval interface - discovered when writing generators)

### Generation

- [x] Write tests for XDC generator (`tests/test_xdc.py`)
- [x] Implement XDC generator (`io_gen/generate/xdc.py`)
- [x] Write tests for Verilog top-level generator (`tests/test_verilog_top.py`)
- [x] Implement Verilog top-level generator (`io_gen/generate/verilog_top.py`)
- [x] Write tests for buffer instantiation helpers (`tests/test_verilog_ioring.py`)
- [x] Implement buffer instantiation helpers (`io_gen/generate/verilog_ioring.py`)
- [x] Write tests for `_generate_verilog_ioring_ports`
- [x] Implement `_generate_verilog_ioring_ports`
- [x] Implement `generate_verilog_ioring` assembler
- [x] Write tests for VHDL top-level generator (`tests/test_vhdl_top.py`)
- [x] Implement VHDL top-level generator (`io_gen/generate/vhdl_top.py`)
- [x] Write tests for VHDL IO ring generator (`tests/test_vhdl_ioring.py`)
- [x] Implement VHDL IO ring generator (`io_gen/generate/vhdl_ioring.py`)

## CLI

- [x] `--validate-only` flag
- [x] `--rtl-only` flag
- [x] `--xdc-only` flag
- [x] Per-stage progress feedback via `print()` in `pipeline.py`

## Validation - Pending Checks

- [x] Signal name format - checked in `run_pipeline` after target language is known (`io_gen/identifiers.py`)
- [x] Top level HDL module name validated as legal identifier
- [x] Non-ASCII characters in YAML rejected before parsing (`_check_non_ascii` in `io_gen/checks.py`)
- [x] Instance name format - the optional `instance` field becomes an HDL
      identifier in the IO ring. Must be validated as a legal identifier
      before generation. Same language considerations as signal names.

## Housekeeping

- [x] Delete `io_gen/generate/verilog.py` - dead leftover from before the split
      into `verilog_top.py` and `verilog_ioring.py`; syntactically broken, not
      imported anywhere
- [x] Remove duplicate `_build_ioring_port_list` stub from `verilog_ioring.py`
      (lines 21-31) - real implementation lives in `common.py`
- [x] Update `generation.md` module layout - add `common.py` and `formatting.py`,
      remove `vhdl_top.py` and `vhdl_ioring.py` (or mark them pending)
- [x] Update "skipped by generators" language in `generation.md` and `verilog_top.py`
      docstrings - `generate: false` signals are excluded at table construction,
      not by the generators themselves

## Deferred

- [ ] Add support for marking inputs as clocks and inserting BUFG into the design
- [ ] Create a Basys3 YAML and validate XDC output using a Vivado I/O Planning
      project (UG899). This project type operates purely at the pin assignment
      level - no RTL needed - and Vivado validates constraints directly against
      the device model. Catches pin assignment and IOSTANDARD violations without
      a synthesis run. Preferred integration test for XDC correctness.
- [ ] IOSTANDARD compatibility with bank VCCO voltage - left to a future
      validation pass or the downstream toolchain
