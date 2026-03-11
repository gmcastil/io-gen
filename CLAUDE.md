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

## Context Loading

At the start of every session, read all files in the `docs/` folder before
doing anything else. These files are the source of truth for design decisions,
schema rules, and pending work. Also read all files in `schema/` and `examples/`,
then run a consistency check across all three and report any issues before proceeding.

## Current Project State

This is a code generation pipeline that will:

- Read FPGA pin constraint data from a YAML file
- Generate XDC constraint files, VHDL or Verilog port definitions, IO ring
  code, IO primitive instantiations, and signal declarations
- Output goes to files in a directory specified at runtime

The pipeline design is documented in `README.md` and the stage-level
docs it references. The schema is defined in `schema/schema.json` and
documented in `docs/schema.md`. The data structures are settled - see the
stage docs for details.

## What Is In Archive

The `archive/` folder contains previous implementation attempts and should be ignored.

## Conventions

Output naming and structural conventions are defined in `docs/conventions.md`.
This is the source of truth - do not infer conventions from examples alone.

## Examples

The files in `examples/` are canonical reference output. They represent
agreed-upon correct structure and naming. Do not modify them without
explicit discussion.

## Formatting

The generator produces readable, indented output but does not enforce
project-specific style. Users may post-process output with:
- Verilog: verible-verilog-format
- VHDL: vsg --fix

Do not add formatter invocation to the pipeline.

## Domain Knowledge

### Known Edge Cases

- TBD - to be filled in as we discover them

### Invalid Assumptions From Previous Attempts

- TBD - to be filled in as we identify them

## Current Focus

- [x] Review and finalize the JSON schema / data model
- [x] Define the data structures that need to be produced
- [ ] Document each pipeline stage interface (in progress)
- [ ] Write tests for each interface
- [ ] Implement one stage at a time

## Definitions

- **Pin** - a physical FPGA pin with a name, bank, IOSTANDARD, and signal name
- **Bank** - a group of pins sharing power and (usually) IOSTANDARD characteristics
- **XDC constraints** - Xilinx Design Constraints file containing pin assignments and IO standards
- **IO ring** - the boundary logic between the top-level ports and internal signals

## Coding

- Python is the implementation language
- `top` is a positional CLI argument, not a YAML field
- ASCII only. Do not include non-ASCII characters, emojis, or unicode characters
