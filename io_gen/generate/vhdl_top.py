from pytest import Metafunc
from io_gen.tables import SignalTable
from io_gen.tables.meta_table import MetaTable

from .formatting import indent_join, indent_strings

from .common import (
    VHDL_DIRECTIONS,
    get_signal_top_ports,
    get_signal_nets,
    get_signal_ioring_ports,
)


def generate_vhdl_top(
    signal_table: SignalTable, meta_table: MetaTable, top: str
) -> str:
    """Generate the complete VHDL top-level entity and architecture as a string.

    Assembles the library clauses, entity declaration, port list, internal signal
    declarations, and IO ring instantiation by calling private helpers in order.
    """
    arch = meta_table.architecture
    rtl = []
    rtl.append("library ieee;")
    rtl.append("use ieee.std_logic_1164.all;")
    rtl.append("")
    rtl.append(f"entity {top} is")
    rtl.append("    -- generic (")
    rtl.append("    -- )")
    rtl.append("    port (")
    rtl.append(_generate_vhdl_ports(signal_table))
    rtl.append("    );")
    rtl.append(f"end entity {top};")
    rtl.append("")
    rtl.append(f"architecture {arch} of {top} is")
    rtl.append("")
    rtl.append(_generate_vhdl_signals(signal_table))
    rtl.append("")
    rtl.append("begin")
    rtl.append("")
    rtl.append(_generate_vhdl_ioring_inst(signal_table, top))
    rtl.append("")
    # Add a newline here so that the file ends appropriately
    rtl.append(f"end architecture {arch};\n")

    return "\n".join(rtl)


def _generate_vhdl_ports(signal_table: SignalTable) -> str:
    """Generate the indented port declaration list for a VHDL entity.

    Returns a string of indented, semicolon-terminated port declarations suitable
    for inclusion inside an entity header. Pad-facing naming convention is used:
    single-ended signals get _pad, differential signals get _p and _n legs.
    An optional comment.hdl string is emitted as a -- line before each signal's
    port(s). The last port declaration has no trailing semicolon.
    """

    # Need to identify the largest length in the LHS of the port declaration
    # then round it up so that there is always space between the last character
    # of the longest name and the colon such that the colon lands on a 4 space
    # tab stop.
    port_names = []
    for sig in signal_table:
        for port in get_signal_top_ports(sig):
            port_names.append(port["name"])

    longest_name = len(max(port_names, key=len))
    name_len = ((longest_name // 4) + 1) * 4

    ports = []
    for sig_index, sig in enumerate(signal_table):
        comment_str = sig["comment"].get("hdl", None)
        if comment_str:
            ports.append(f"-- {comment_str}")

        # Get all the ports for this signal
        sig_ports = get_signal_top_ports(sig)
        # Need to keep track of the last item so that on the last signal in the
        # table and the last port, we can omit the comma
        last_index = len(sig_ports) - 1
        for port_index, port in enumerate(sig_ports):
            # Craft the string to go on the LHS of the colon
            lhs_line = f"{port['name']:<{name_len}}"

            # Create the string for the RHS of the colon
            direction = VHDL_DIRECTIONS[port["direction"]]
            if port["is_bus"]:
                rhs_line = (
                    f"{direction:<6}std_logic_vector({port['width'] - 1} downto 0)"
                )
            else:
                rhs_line = f"{direction:<6}std_logic"
            # Now append a semicolon onto everyone except the last line
            if last_index != port_index or sig_index != len(signal_table) - 1:
                rhs_line = f"{rhs_line};"
            # Assemble the actual line
            ports.append(f"{lhs_line}: {rhs_line}")

    return indent_join(ports, 2)


def _generate_vhdl_signals(signal_table: SignalTable) -> str:
    """Generate the internal signal declarations for a VHDL top-level architecture.

    Returns a string of indented signal declarations for fabric-facing signals.
    Signals with bypass: true are excluded - they have no internal counterpart.
    Tristate signals (iobuf) expand to three signals: <name>_i, <name>_o, <name>_t.
    All other signals use the bare signal name regardless of buffer type.
    """

    lhs_sig_strings = []
    rhs_sig_strings = []

    for sig in signal_table.active():
        for net in get_signal_nets(sig):
            # Craft the string to go on the LHS of the colon
            lhs_sig_strings.append(f"signal {net['name']}")

            # The signal dimensions and types for the RHS are much easier to create
            if net["is_bus"]:
                rhs_sig_strings.append(
                    f"std_logic_vector({net['width'] - 1} downto 0);"
                )
            else:
                rhs_sig_strings.append("std_logic;")

    # An empty IO ring is a possibility
    if not lhs_sig_strings:
        return ""

    # Now we need to identify the largest length in the LHS of the signal declaration
    # then round it up so that there is always space between the last character of the
    # longest name and the colon such that the colon lands on a 4 space tab stop
    longest_name = len(max(lhs_sig_strings, key=len))
    name_len = ((longest_name // 4) + 1) * 4

    sig_decls = []
    for lhs, rhs in zip(lhs_sig_strings, rhs_sig_strings):
        sig_decls.append(f"{lhs:<{name_len}}: {rhs}")

    return indent_join(sig_decls)


def _generate_vhdl_ioring_inst(signal_table: SignalTable, top: str) -> str:
    """Generate the IO ring entity instantiation for a VHDL top-level architecture.

    Returns a string containing the IO ring instance with port connections
    mapping pad-facing top-level ports and internal signals to the IO ring ports.
    Signals with bypass: true are excluded.
    """
    inst = []
    inst.append(f"{top}_io_i0 : entity work.{top}_io")
    inst.append("-- generic map (")
    inst.append("-- )")
    inst.append("port map (")

    inst = indent_strings(inst, 1)

    # Need to collect all the ports in the instance and find the longest name, then
    # round it up so that there is always space between the last character of the longest
    # name and the port assignment operator (=>) and also such that the port assignment
    # operator lands on a 4 space tab stop
    ioring_ports = []
    for sig in signal_table.active():
        for port in get_signal_ioring_ports(sig):
            ioring_ports.append(port["name"])

    longest_name = len(max(ioring_ports, key=len))
    name_len = ((longest_name // 4) + 1) * 4

    # Now iterate the list of ports in the IO ring and format them with the calculated
    # amount of whitespace, join the port map itself into one already indented string,
    # and then add to the instantiation string
    port_strings = [f"{name:<{name_len}}=> {name}" for name in ioring_ports]
    inst.append(indent_join(port_strings, 2, ",\n"))

    inst.append("    );")

    return "\n".join(inst)
