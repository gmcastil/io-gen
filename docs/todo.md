# Todo

## Design

- [x] Define the signal table dataclass fields (see signal_table.md)
- [ ] Define the pin table dataclass fields (see pin_table.md)

## Implementation

- [ ] Write the validator
- [ ] Write tests for table construction
- [ ] Write tests for each generator

## CLI

- [ ] Stdout mode
- [ ] `--validate-only` flag
- [ ] `--rtl-only` flag
- [ ] `--xdc-only` flag

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
