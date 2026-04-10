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
- I commonly ask questions to confirm my understanding - when asking you to
  explain something, I frequently translate it in my mind and communicate it
  back.
- Please suggest improvements in the code as we go, focusing on common
  programming patterns, idiomatic code that is easy to test and maintain

## How We Work Together

1. **Design first** - we discuss and agree on interfaces and data structures before any code is written
2. **Tests second** - we write tests that define the expected behavior of each interface
3. **Implementation last** - only once tests exist do we write code to make them pass
4. **One thing at a time** - we complete one pipeline stage before moving to the next

## Context Loading

At the start of every session, read all files in the `docs/` folder before
doing anything else. These files are the source of truth for design decisions,
schema rules, and pending work. Also read all files in `io_gen/schema/` and
`examples/`, then run a consistency check across all three and report any
issues before proceeding. `docs/devlog.md` is part of this - read it to
understand recent decisions and history before engaging.

## Code Review Style

When reviewing code, apply the standards of a Python core developer:

- Prefer the simplest correct implementation - no unnecessary abstraction
- Flag violations of PEP 8 and PEP 20 (Zen of Python)
- Point out deviations from idiomatic Python (e.g., prefer `x is None` over
  `x == None`, use `dict.get()` over guarded access, prefer comprehensions
  over maps/filters where readability is equal or better, etc.)
- Prefer built-ins and stdlib over custom solutions where they exist
- Flag anything that would fail a CPython PR review: missing or imprecise type
  hints, unclear variable names, overly complex expressions, unnecessary
  intermediate variables
- Be direct about problems - do not soften criticism

## Session Close

When wrapping up a session, remind the user to add an entry to `docs/devlog.md`
summarizing what was decided or changed. Entries go at the top, reverse
chronological. Include the relevant commit hash if a commit was made.

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

### Deferred Buffer Types

- `iobufds` - differential tristate buffer. Valid use case, intentionally omitted
  from the buffer enum until the base set (ibuf, obuf, ibufds, obufds, iobuf) is
  working end-to-end. Do not add it without being asked.

### Invalid Assumptions From Previous Attempts

- TBD - to be filled in as we identify them

### Design Decisions

- **No bank inheritance** - there is no bank-level IOSTANDARD inheritance. Every
  signal except `generate: false` must carry an explicit `iostandard`. This was
  a deliberate simplification - the target user is disciplined enough to be
  explicit. The `banks` map and `bank` field were removed from the schema entirely.
- **`bypass: true` prohibits `buffer`** - a signal with `bypass: true` must not
  include a `buffer` field. This is enforced by the schema. Providing `buffer`
  with `bypass: true` is a contradiction - bypass means an external component
  (e.g., Xilinx IP) provides the buffer, and specifying one in the YAML would
  silently mislead the user.
- **No `BankTable`** - an earlier iteration included a `BankTable` to support
  bank-level IOSTANDARD inheritance. It was removed along with the banks concept.
  `bank_table.py` no longer exists.
- **Instance names are always resolved in the signal table** - `instance` in a
  signal table row is always a `str`, never `None`. `build_signal_table()` either
  uses the user-supplied override or auto-generates `<buffer_type>_<signal_name>`.
  `bypass: true` signals have no buffer and no IO ring instantiation, so their
  `instance` is `None`. The pin table appends `_i<N>` to produce the final name.
  Generators read the pin table directly and never infer anything.
- **Instance indexing is always `_i<N>`** - there is no special case for scalars.
  A scalar gets `_i0`. A bus gets `_i0` through `_iN`. This applies to both
  auto-generated and user-supplied instance names.

## Current Focus

- [x] Review and finalize the JSON schema / data model
- [x] Define the data structures that need to be produced
- [x] Document each pipeline stage interface
- [x] Write tests for each interface
- [x] Implement one stage at a time

### Validation Stage Status

- [x] Structural validation implemented and tested (`io_gen/validate.py`)
- [x] Semantic validation fully implemented (`io_gen/checks.py`)
- [x] All check functions tested in `tests/test_checks.py`)
- [x] Structural and integration tests in `tests/test_validate.py`
- [x] Non-ASCII check implemented (`_check_non_ascii` in `io_gen/checks.py`)
- [x] Enriched jsonschema error messages with signal name (`io_gen/validate.py`)
- `io_gen/exceptions.py` defines `ValidationError` in isolation (no imports)
- `io_gen/checks.py` contains all `_check_*` functions and `_get_pin_names_from_signal` helper
- `io_gen/validate.py` orchestrates structural and semantic validation only

### Table Construction Stage Status

- [x] `SignalTable` interface designed and documented (`docs/signal_table.md`)
- [x] `io_gen/tables/` package implemented and tested
- [x] `MetaTable` implemented and tested (`tests/test_meta_table.py`)
- [x] `SignalTable` and `build_signal_table()` implemented and tested (`tests/test_signal_table.py`)
- [x] `PinTable` and `build_pin_table()` implemented and tested (`tests/test_pin_table.py`, `tests/test_flatten.py`)

Key design decisions:

- `SignalTable` is a thin wrapper class over `list[dict]`
- `PinTable` is a thin wrapper class over `dict[str, list[dict]]`, keyed by signal name
- Rows are plain dicts with variable shape (three shapes - see `docs/signal_table.md`)
- Each factory function lives in the same module as its class
- Tables are a package: `io_gen/tables/`
  - `io_gen/tables/signal_table.py` - `SignalTable`, `_build_signal_table()`, `_signal_is_scalar()`, `_signal_is_differential()`
  - `io_gen/tables/pin_table.py` - `PinTable`, `_build_pin_table()`, `_pin_is_differential()`
  - `io_gen/tables/meta_table.py` - `MetaTable`, `_build_meta_table()`
  - `io_gen/tables/__init__.py` - re-exports all classes and private helpers
- `_signal_is_scalar(sig)` distinguishes scalar vs. bus (single pin vs. array)
- `_signal_is_differential(sig)` distinguishes SE vs. differential pair (`pins` vs. `pinset`) — orthogonal to scalar/bus
- `_pin_is_differential(pin)` distinguishes SE vs. differential at the pin row level (used in XDC generator)
- `PinTable.__getitem__(name)` is the public retrieval interface for generators — use `pt[sig["name"]]`

### Generation Stage Status

- [x] XDC generator implemented and tested (`io_gen/generate/xdc.py`, `tests/test_xdc.py`)
- [x] Verilog top-level generator fully implemented and tested (`io_gen/generate/verilog_top.py`, `tests/test_verilog_top.py`)
- [x] Verilog IO ring fully implemented and tested (`io_gen/generate/verilog_ioring.py`, `tests/test_verilog_ioring.py`)
- [x] `generate_verilog_ioring` assembler complete
- [ ] VHDL generators (deferred until Verilog is validated end-to-end in Vivado)

Key design decisions:

- Generators live in `io_gen/generate/`, split by output file and language:
  - `xdc.py` - `generate_xdc(st, pt)`
  - `verilog_top.py` - `generate_verilog_top(st, top)` + private helpers
  - `verilog_ioring.py` - `generate_verilog_ioring(st, pt, top)` + private helpers
  - `common.py` - `_get_signal_top_ports`, `_get_signal_ioring_ports`, `_get_signal_nets`, `_get_ioring_header`
  - `formatting.py` - `_indent_join`
  - `vhdl_top.py`, `vhdl_ioring.py` - VHDL counterparts (pending)
- Buffer dispatch uses `_INSTANTIATE_BUFFERS` and `_INFER_BUFFERS` dicts keyed by buffer type
- `infer: true` signals use a single `assign` statement — no pin table lookup needed
- Generators never see `generate: false` signals — filtered at signal table construction

### CLI and Pipeline Status

- [x] `io_gen/cli.py` implemented with argparse — `--top`, `--lang`, `--output`, `--validate-only`, `--rtl-only`, `--xdc-only`
- [x] `io_gen/pipeline.py` (`run_pipeline`) implemented — dir creation, identifier validation, table construction, file writing with status output
- [x] `io_gen/identifiers.py` — `_is_valid_verilog_identifier` and `_is_valid_vhdl_identifier` both implemented
- [x] Entry point `io-gen` registered in `pyproject.toml`
- [x] Makefile updated to run `pip install -e .` in venv stamp target
- [x] First successful end-to-end run against a real board YAML

## Definitions

- **Pin** - a physical FPGA pin with a name, bank, IOSTANDARD, and signal name
- **Bank** - a group of pins sharing power and (usually) IOSTANDARD characteristics
- **XDC constraints** - Xilinx Design Constraints file containing pin
  assignments and IO standards
- **IO ring** - the boundary logic between the top-level ports and internal signals

## Distribution

This tool is intended to be installable via pip, distributed via GitHub.
Keep the following in mind throughout development:

- Schema files live inside `io_gen/schema/` so they are included in the installed
  package. Do not move them back to the repo root.
- Use `importlib.resources` to locate schema files at runtime. Do not use relative
  paths like `../../schema/` that break when the package is installed.
- Runtime dependencies belong in `pyproject.toml` under `[project] dependencies`.
  Do not add runtime dependencies only to `requirements.txt`.
- `pytest` and `pytest-cov` are dev-only and must not appear in `[project] dependencies`.
- The terminal command is `io-gen`, defined in `[project.scripts]`.
- Installation methods:
  - From GitHub: `pip install git+https://github.com/gmcastil/io-gen.git`
  - From a local clone: `pip install .`
  - Editable install for development: `pip install -e .`

## Testing Conventions

- No test classes - use plain `test_` functions throughout
- Parametrized cases are defined as module-level lists of `(name, ...)` tuples
  and passed to `@pytest.mark.parametrize` using `pytest.param(..., id=name)`
- Test data is inline dicts, not loaded from YAML files or example fixtures.
  `test_validate.py` uses YAML strings as an exception because `validate()`
  requires a file path - all other tests work directly with dicts
- Sections within a test file are separated by comment banners matching the
  style in existing test files
- For table construction tests, `generate:false` row shapes are asserted both
  positively (required keys present with correct values) and negatively (keys
  that belong only to `generate:true` rows are explicitly absent)

## Coding

- Python is the implementation language
- Follow PEP 8 for all code style (naming, spacing, line length, imports, etc.)
  with the understanding that formatting is enforced by the black formatting
  plugin.
- `top` is a positional CLI argument, not a YAML field
- ASCII only. Do not include non-ASCII characters, emojis, or unicode characters
- Type hints are required on all functions and methods in both application and test code
- When iterating over signals, use `sig` as the loop variable, not `signal`
  (avoid shadowing the standard library `signal` module)
- When reviewing code, check that variable and parameter names are consistent
  across the codebase (e.g., the same concept is not called `sig` in one place
  and `signal` in another)
