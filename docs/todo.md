# Todo

## Design

- [x] Define the signal table dataclass fields (see signal_table.md)
- [x] Define the pin table dataclass fields (see pin_table.md)

## Implementation

### Validation

- [x] Write exhaustive unit tests for the buffer/direction compatibility checking logic
- [x] Write exhaustive unit tests for the buffer/pin strategy compatibility checking logic
- [x] Write the validator
- [ ] Cache the JSON schema registry as a module global in validate.py

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
- [ ] Write tests for Verilog top-level generator (`tests/test_verilog_top.py`)
- [ ] Implement Verilog top-level generator (`io_gen/generate/verilog_top.py`)
- [ ] Write tests for Verilog IO ring generator (`tests/test_verilog_ioring.py`)
- [ ] Implement Verilog IO ring generator (`io_gen/generate/verilog_ioring.py`)
- [ ] Write tests for VHDL top-level generator (`tests/test_vhdl_top.py`)
- [ ] Implement VHDL top-level generator (`io_gen/generate/vhdl_top.py`)
- [ ] Write tests for VHDL IO ring generator (`tests/test_vhdl_ioring.py`)
- [ ] Implement VHDL IO ring generator (`io_gen/generate/vhdl_ioring.py`)

## CLI

- [ ] Stdout mode
- [ ] `--validate-only` flag
- [ ] `--rtl-only` flag
- [ ] `--xdc-only` flag
- [ ] Per-stage progress feedback - consider a callback passed from CLI to pipeline
      so the pipeline stays decoupled from presentation

## Validation - Pending Checks

- [ ] Signal name format - must be a valid HDL identifier. Rules are
      language-specific (Verilog and VHDL differ), so this check should
      run after the target language is known or enforce the intersection
      of both sets of rules.
- [ ] Instance name format - the optional `instance` field becomes an HDL
      identifier in the IO ring. Must be validated as a legal identifier
      before generation. Same language considerations as signal names.
- [ ] Top level HDL module name needs to be valid VHDL or Verilog
- [ ] Signal and signal + instance should be capped, maybe? Future discussion

## Housekeeping

- [x] Delete `io_gen/generate/verilog.py` - dead leftover from before the split
      into `verilog_top.py` and `verilog_ioring.py`; syntactically broken, not
      imported anywhere
- [x] Remove duplicate `_build_ioring_port_list` stub from `verilog_ioring.py`
      (lines 21-31) - real implementation lives in `common.py`
- [ ] Update `generation.md` module layout - add `common.py` and `formatting.py`,
      remove `vhdl_top.py` and `vhdl_ioring.py` (or mark them pending)
- [ ] Update "skipped by generators" language in `generation.md` and `verilog_top.py`
      docstrings - `generate: false` signals are excluded at table construction,
      not by the generators themselves

## Deferred

- [ ] Add support for marking inputs as clocks and inserting BUFG into the design
- [ ] Once the tool is working, make a legit YAML for a Basys 3 that can be
      used along with a basic user core of keepers so that the example can be
      checked in Vivado. This actually becomes an end to end integration test
      that can be automated. Do something like store a basic user core with all
      the different kinds of IO in it, run the tool, capture the output, use sed
      or something to paste the user core instance into the top level module,
      and then run synthesis -> bitstream, generate a utilization report and
      check it to make sure that we have the IO that we think we do.
- [ ] IOSTANDARD compatibility with bank VCCO voltage - left to a future
      validation pass or the downstream toolchain
