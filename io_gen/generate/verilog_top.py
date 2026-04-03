from io_gen.tables import SignalTable

from .formatting import _format_port_block

from .common import _get_signal_top_ports, _get_signal_nets


def generate_verilog_top(signal_table: SignalTable) -> str:
    """Generate the complete Verilog top-level module as a string.

    Assembles the module declaration, port list, internal wire declarations,
    and IO ring instantiation by calling private helpers in order.
    Signals with generate: false are excluded from all output.
    """
    pass


def _generate_verilog_ports(signal_table: SignalTable) -> str:
    """Generate the indented port declaration list for a Verilog module.

    Returns a string of indented, comma-terminated port declarations suitable
    for inclusion inside a module header. Pad-facing naming convention is used:
    single-ended signals get _pad, differential signals get _p and _n legs.
    An optional comment.hdl string is emitted as a // line before each signal's
    port(s). The last port declaration has no trailing comma.
    Signals with generate: false are excluded.
    """
    ports = []
    for sig in signal_table:

        # The strategy here is to create the entire list of ports and comments without any indent, then once it's
        # finished, iterate the result, add commas at the end of all but the last one and indent everything along the
        # way (use the fact that comments start with # before indenting, and then add the commas).

        # HDL comments if present
        comment_str = sig["comment"].get("hdl", None)
        if comment_str:
            ports.append(f"// {comment_str}")

        # Get the one or two ports for this signal
        for port in _get_signal_top_ports(sig):
            # Port direction
            if port["direction"] == "in":
                direction_str = "input".ljust(7)
            elif port["direction"] == "out":
                direction_str = "output".ljust(7)
            else:
                direction_str = "inout".ljust(7)

            # Net type and width block
            if port["is_bus"]:
                width_str = f"wire [{port['width'] - 1}:0]".ljust(12)
            else:
                width_str = f"wire".ljust(12)

            # Now assemble the string for the entire port
            ports.append(f"{direction_str}{width_str}{port['name']}")

    # Now indent and append commas to (almost) every line
    return "\n".join(_format_port_block(ports, 1, "verilog"))


def _generate_verilog_wires(signal_table: SignalTable) -> str:
    """Generate the internal wire declarations for a Verilog top-level module.

    Returns a string of indented wire declarations for fabric-facing signals.
    Signals with bypass: true are excluded - they have no internal counterpart.
    Tristate signals (iobuf) expand to three wires: <name>_i, <name>_o, <name>_t.
    All other signals use the bare signal name regardless of buffer type.
    Signals with generate: false are excluded.
    """
    wires = []
    for sig in signal_table:
        # Skip signals that aren't to be generated or don't appear in the IO ring
        sig_nets = _get_signal_nets(sig)

        if not sig_nets:
            continue

        for net in sig_nets:
            name = net["name"]
            width = net["width"]

            # Can get this now and then we'll pad to 8 columns later
            if net["is_bus"]:
                dim = f"[{width - 1}:0]"
            else:
                dim = ""

            # Formatting is simple - 4 space indent, 8 columsn for the net type,
            # 8 columns for the net dimension, then the port name
            wires.append(f"{'':<4}{'wire':<8}{dim:<8}{name};")

    return "\n".join(wires)


def _generate_verilog_ioring_inst(signal_table: SignalTable) -> str:
    """Generate the IO ring module instantiation for a Verilog top-level module.

    Returns a string containing the IO ring instance with port connections
    mapping pad-facing top-level ports and internal wires to the IO ring ports.
    Signals with generate: false are excluded.
    """
    pass
