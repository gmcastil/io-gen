# Todo

## Design

- [ ] Define the signal table dataclass fields (see signal_table.md)
- [ ] Define the pin table dataclass fields (see pin_table.md)
- [ ] Define the exact error message format for ValidationError

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

- [ ] IOSTANDARD compatibility with bank VCCO voltage - left to a future
      validation pass or the downstream toolchain
