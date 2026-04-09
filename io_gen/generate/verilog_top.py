from io_gen.tables import SignalTable

from .formatting import _indent_join

from .common import (
    _get_signal_top_ports,
    _get_signal_nets,
    _get_signal_ioring_ports,
    VLOG_DIRECTIONS,
)


def generate_verilog_top(signal_table: SignalTable, top: str) -> str:
    """Generate the complete Verilog top-level module as a string.

    Assembles the module declaration, port list, internal wire declarations,
    and IO ring instantiation by calling private helpers in order.
    """
    rtl = []
    rtl.append(f"module {top} //#(")
    rtl.append(f"//)")
    rtl.append(f"(")
    rtl.append(_generate_verilog_ports(signal_table))
    rtl.append(f");")
    rtl.append(f"")
    rtl.append(_generate_verilog_wires(signal_table))
    rtl.append(f"")
    rtl.append(_generate_verilog_ioring_inst(signal_table, top))
    rtl.append(f"")
    # Add a newline here so that the file ends appropriately
    rtl.append(f"endmodule\n")

    return "\n".join(rtl)


def _generate_verilog_ports(signal_table: SignalTable) -> str:
    """Generate the indented port declaration list for a Verilog module.

    Returns a string of indented, comma-terminated port declarations suitable
    for inclusion inside a module header. Pad-facing naming convention is used:
    single-ended signals get _pad, differential signals get _p and _n legs.
    An optional comment.hdl string is emitted as a // line before each signal's
    port(s). The last port declaration has no trailing comma.
    """
    ports = []
    for sig_index, sig in enumerate(signal_table):
        # The strategy here is to create the entire list of ports and comments without any indent, then once it's
        # finished, iterate the result, add commas at the end of all but the last one and indent everything along the
        # way (use the fact that comments start with # before indenting, and then add the commas).

        # HDL comments if present
        comment_str = sig["comment"].get("hdl", None)
        if comment_str:
            ports.append(f"// {comment_str}")

        # Get all the ports for this signal
        sig_ports = _get_signal_top_ports(sig)
        # Need to keep track of the last item so that on the last signal in the
        # table and the last port, we can drop the comma
        last_index = len(sig_ports) - 1
        for port_index, port in enumerate(sig_ports):
            direction = VLOG_DIRECTIONS[port["direction"]]
            if port["is_bus"]:
                width = f"[{port['width'] - 1}:0]"
            else:
                width = f""
            dim = f"wire {width}"
            # Every port but the last port of the last signal gets a comma
            if last_index == port_index and sig_index == len(signal_table) - 1:
                suffix = f""
            else:
                suffix = f","
            line = f"{direction:<8}{dim:<16}{port['name']}{suffix}"
            ports.append(line)

    return _indent_join(ports, 1, "\n")


def _generate_verilog_wires(signal_table: SignalTable) -> str:
    """Generate the internal wire declarations for a Verilog top-level module.

    Returns a string of indented wire declarations for fabric-facing signals.
    Signals with bypass: true are excluded - they have no internal counterpart.
    Tristate signals (iobuf) expand to three wires: <name>_i, <name>_o, <name>_t.
    All other signals use the bare signal name regardless of buffer type.
    """
    wires = []
    for sig in signal_table:
        # Skip bypass signals - they have no internal wire
        sig_nets = _get_signal_nets(sig)

        if not sig_nets:
            continue

        for net in sig_nets:
            name = net["name"]
            width = net["width"]

            # Can get this now and then we'll pad to 8 columns later
            if net["is_bus"]:
                width = f"[{width - 1}:0]"
            else:
                width = ""
            dim = f"wire {width}"
            # Formatting is simple - 4 space indent, 8 columsn for the net type,
            # 8 columns for the net dimension, then the port name
            wires.append(f"{dim:<16}{name};")

    return _indent_join(wires, 1, "\n")


def _generate_verilog_ioring_inst(signal_table: SignalTable, top: str) -> str:
    """Generate the IO ring module instantiation for a Verilog top-level module.

    Returns a string containing the IO ring instance with port connections
    mapping pad-facing top-level ports and internal wires to the IO ring ports.
    Signals with generate: false are excluded.
    """
    inst = []
    inst.append(f"{'':<4}{top}_io //#(")
    inst.append(f"{'':<4}//)")
    inst.append(f"{'':<4}{top}_io_i0 (")

    ioring_ports = list()

    # Get all of the names for every signal in the IO ring
    for sig in signal_table:
        # Skip top level signals that do not go to the IO ring
        if sig["bypass"]:
            continue
        for port in _get_signal_ioring_ports(sig):
            ioring_ports.append(port["name"])

    # Now calculate how many spaces we need for the port name in the instance by
    # getting the length of the longest name
    longest_name = len(max(ioring_ports, key=len))
    # Then account for the '.' in the length of the first field and round up to
    # the next multiple of 4 so we can keep all of our columns aligned nicely
    name_len = (((longest_name + 1) // 4 + 1) * 4) - 1

    # Now iterate the list of ports in the IO ring and format them with a 4 space
    # indent, followed by another 4 spaces, then the calculated max length rounded up,
    # then the same port name again inside parens, and a trailing comma, except on
    # the last port
    for index, name in enumerate(ioring_ports):
        if index == len(ioring_ports) - 1:
            suffix = ""
        else:
            suffix = ","
        inst.append(f"{'':<8}.{name:<{name_len}}({name}){suffix}")

    # Now attach the trailing parenthesis on its own
    inst.append(f"{'':<4});")

    return "\n".join(inst)
