# Todo

## Design

- [x] Define the signal table dataclass fields (see signal_table.md)
- [x] Define the pin table dataclass fields (see pin_table.md)

## Implementation

- [ ] Write the validator
- [ ] Cache the JSON schema registry as a module global in validate.py
- [ ] Write exhaustive unit tests for the buffer/direction compatibility checking logic
- [ ] Write exhaustive unit tests for the buffer/pin strategy compatibility checking logic
- [ ] Write tests for table construction
- [ ] Write tests for each generator

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
