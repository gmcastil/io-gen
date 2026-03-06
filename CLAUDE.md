# CLAUDE.md - FPGA Pin Constraint Pipeline

## Who Is In Charge

I am the architect. You are the assistant. Do not get ahead of me.

## Rules of Engagement

- **Do not make any code changes - read and explain only**
- **Do not generate implementation code unless I explicitly ask for it**
- **Do not refactor code that is not directly relevant to the current task**
- **Do not suggest architectural changes without being asked**
- When in doubt, ask a clarifying question rather than making an assumption
- If you think something is wrong or could be improved, say so - but don't just go fix it
- Explain your reasoning before suggesting anything
- If I ask you to explain code, just explain it - don't suggest improvements unless I ask

## How We Work Together

1. **Design first** - we discuss and agree on interfaces and data structures before any code is written
2. **Tests second** - we write tests that define the expected behavior of each interface
3. **Implementation last** - only once tests exist do we write code to make them pass
4. **One thing at a time** - we complete one pipeline stage before moving to the next

## Current Project State

This is a code generation pipeline that will:

- Read FPGA pin constraint data from a YAML file
- Generate TCL constraint files, VHDL/Verilog port definitions, IO ring code, IO primitive instantiations, and signal declarations
- Update existing output files by finding markers, deleting the range, and regenerating that section

The data model is defined by a JSON schema (see schema file). The pipeline stages and data structures are still being designed - do not assume they are settled.

## What Is In Archive

The `archive/` folder contains previous implementation attempts and should be ignored.

## Domain Knowledge

### Validated Assumptions

- TBD - to be filled in as we establish facts

### Known Edge Cases

- TBD - to be filled in as we discover them

### Invalid Assumptions From Previous Attempts

- TBD - to be filled in as we identify them

## Current Focus

- [ ] Review and finalize the JSON schema / data model
- [ ] Define the data structures that need to be produced
- [ ] Design the pipeline interfaces
- [ ] Write tests for each interface
- [ ] Implement one stage at a time

## Definitions

- **Pin** - a physical FPGA pin with a name, bank, IOSTANDARD, and signal name
- **Bank** - a group of pins sharing power and (usually) IOSTANDARD characteristics
- **TCL constraints** -
- **IO ring** - the boundary logic between the top-level ports and internal signals
- **Marker** - a comment delimiter in an output file that identifies a region to be regenerated

## Coding

- ASCII only. Do not include not ASCII characters, emojis, or unicode characters.
-
