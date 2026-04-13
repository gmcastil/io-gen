# Examples

## Purpose

The files in this directory serve two purposes: they demonstrate how to structure
a YAML input file for `io-gen`, and they provide the foundation for an
end-to-end hardware validation flow that proves the tool produces correct,
synthesizable output.

The YAML file is the primary reference for how signals are described. The JSON
schema in `io_gen/schema/` is the authoritative definition of what is and is not
valid - the example YAML is an illustration of the schema in use, not a
substitute for reading it. Every major signal type is represented: scalar and
bus, single-ended and differential, every supported buffer type, inference,
bypass, and generate: false.

---

## End-to-End Hardware Validation

The larger intent of this directory is to support a full demonstration flow:
run `io-gen` against `example.yaml`, take the generated HDL and XDC files, drop
in a minimal user logic core, and push it all the way through Vivado to a
bitstream on real hardware. This is not just a smoke test - it is proof that
the tool instantiates and connects IO buffers correctly, names ports and
instances as documented, and produces output that the Xilinx toolchain accepts
without modification. The target platform for the example design is a Digilent
Basys 3 (Xilinx Artix-7 FPGA: XC7A35T-1CPG236C) built using Vivado 2024.2.

### User Logic Core

The generated IO ring expects fabric-side connections from user logic. To
prevent Vivado from optimizing away IO buffers with unconnected fabric ports, a
minimal user logic core is provided that instantiates LUT-based keepers on
every fabric-facing signal. This is not intended to be a functional logic core;
its purpose is simply to provide sufficient logic to allow each buffer to
persist through from synthesis to bitstream generation, so a final utilization
report can be generated and compared against the expected result.

### Flow

1. Run `io-gen` against `example.yaml` to generate the XDC and HDL files
2. Instantiate the user logic core inside the generated top-level module (TBD
   This will be scripted - a Makefile to generate the entire thing will
   eventually be provided)
3. Run synthesis, implementation, and bitstream generation using the provided
   Tcl scripts (TBD Again, done via makefile)
4. Inspect the utilization report to confirm that every expected IO buffer is
   present, correctly named, and placed on the intended package pin

### What This Demonstrates

- Every buffer type supported by `io-gen` (see [buffers.md](../docs/buffers.md)
  for supported buffer types) is instantiated and survives to bitstream generation
- Port names, instance names, and pin assignments match the conventions
  documented in [conventions.md](../docs/conventions.md)
- The generated XDC constraints are accepted by Vivado without errors or
  critical warnings related to pin assignments or IO standards
- The tool produces output that a real toolchain can consume without any
  hand-editing

### Extensibility

As new IO buffer types and features are added to `io-gen`, the example YAML,
user logic core, and expected utilization report will be extended to cover them.
The flow described here becomes the long-term integration test that no amount of
unit testing can replace - it is the only check that runs the full chain from
YAML description to placed-and-routed hardware.

---

## Files

| File             | Description                                    |
| ---------------- | ---------------------------------------------- |
| `example.yaml`   | Canonical input YAML covering all signal types |
| `example.xdc`    | Expected XDC output                            |
| `example.v`      | Expected Verilog top-level output              |
| `example_io.v`   | Expected Verilog IO ring output                |
| `example.vhd`    | Expected VHDL top-level output                 |
| `example_io.vhd` | Expected VHDL IO ring output                   |
