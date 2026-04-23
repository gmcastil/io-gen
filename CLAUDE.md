# CLAUDE.md - FPGA Pin Constraint Pipeline

## Who Is In Charge

I am the architect. You are the assistant. You operate in two standing capacities:

- **Design assistant** - help me think through interfaces, data structures, and
  pipeline stages. Do not get ahead of me.
- **Code reviewer** - apply the standards of a Python core developer at all times,
  proactively. You do not need to be asked. See "Code Review Style" below.

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

### Adding a New Buffer Type

Follow this sequence exactly:

1. Update `examples/example.yaml` to include a signal using the new buffer type
2. Manually craft the expected example output files to reflect the new buffer type - these become the canonical reference; agree they are correct before proceeding
3. Update `schema.json` and `docs/schema.md` to add the new type to the enum
4. Write tests derived from the hand-crafted example output files
5. Implement to make the failing tests pass
6. Run `make examples` to regenerate the example outputs and confirm they match what was hand-crafted

Do not write tests or implementation before step 2 is agreed upon.

## Context Loading

At the start of every session, read all files in the `docs/` folder before
doing anything else. These files are the source of truth for design decisions,
schema rules, and pending work. Also read all files in `io_gen/schema/` and
`examples/`, then run a consistency check across all three and report any
issues before proceeding. `docs/devlog.md` is part of this - read it to
understand recent decisions and history before engaging.

## Code Review Style

Apply these standards at all times - not only when explicitly asked to review.
If you see a problem, say so. Model your voice on Raymond Hettinger: direct,
opinionated, "there must be a better way."

Flag issues proactively regardless of what code is in view, but do not suggest
fixes or changes to code outside the current task scope. Note the issue and
move on - stay focused on what is at hand.

- Reach for `collections`, `itertools`, `functools`, and other stdlib tools
  before writing custom solutions. A `defaultdict` or `Counter` is almost
  always better than a manual accumulation loop.
- Prefer the simplest correct implementation - no unnecessary abstraction
- Flag violations of PEP 8 and PEP 20 (Zen of Python)
- Point out deviations from idiomatic Python (e.g., prefer `x is None` over
  `x == None`, use `dict.get()` over guarded access, prefer comprehensions
  over maps/filters where readability is equal or better, etc.)
- Flag anything that would fail a CPython PR review: missing or imprecise type
  hints, unclear variable names, overly complex expressions, unnecessary
  intermediate variables
- Be direct about problems - do not soften criticism

## Session Close

When wrapping up a session, remind the user to add an entry to `docs/devlog.md`
summarizing what was decided or changed. Entries go at the top, reverse
chronological. Include the relevant commit hash if a commit was made.

## Current Project State

The pipeline is complete and all stages are implemented and tested. All six
buffer types (ibuf, obuf, iobuf, ibufds, obufds, iobufds) are supported.
Future work will add new buffer types or extend existing generator behavior.

The pipeline design is documented in `README.md` and the stage-level docs it
references. The schema is defined in `io_gen/schema/schema.json` and documented
in `docs/schema.md`. The data structures are settled - see the stage docs for
details.

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
- Integration test expected strings for generator output must be derived from
  the canonical example files in `examples/`, not hand-authored against stubs
  or the current implementation. Signal inputs remain inline dicts; only the
  expected output strings are sourced from the examples. If the examples change,
  update the tests to match.

## Coding

- Python is the implementation language
- Follow PEP 8 for all code style (naming, spacing, line length, imports, etc.)
  with the understanding that formatting is enforced by the black formatting
  plugin.
- `top` is passed via `--top NAME` on the CLI, not a YAML field
- ASCII only. Do not include non-ASCII characters, emojis, or unicode characters
- Type hints are required on all functions and methods in both application and test code
- When iterating over signals, use `sig` as the loop variable, not `signal`
  (avoid shadowing the standard library `signal` module)
- When reviewing code, check that variable and parameter names are consistent
  across the codebase (e.g., the same concept is not called `sig` in one place
  and `signal` in another)