from io_gen.tables import SignalTable

from .formatting import _indent_join

from .common import (
    _get_signal_top_ports,
    _get_signal_nets,
    _get_signal_ioring_ports,
)


def generate_vhdl_top(signal_table: SignalTable, top: str, arch: str) -> str:
    """Generate the complete VHDL top-level entity and architecture as a string.

    Assembles the library clauses, entity declaration, port list, internal signal
    declarations, and IO ring instantiation by calling private helpers in order.
    """
    pass


def _generate_vhdl_ports(signal_table: SignalTable) -> str:
    """Generate the indented port declaration list for a VHDL entity.

    Returns a string of indented, semicolon-terminated port declarations suitable
    for inclusion inside an entity header. Pad-facing naming convention is used:
    single-ended signals get _pad, differential signals get _p and _n legs.
    An optional comment.hdl string is emitted as a -- line before each signal's
    port(s). The last port declaration has no trailing semicolon.
    """
    pass


def _generate_vhdl_signals(signal_table: SignalTable) -> str:
    """Generate the internal signal declarations for a VHDL top-level architecture.

    Returns a string of indented signal declarations for fabric-facing signals.
    Signals with bypass: true are excluded - they have no internal counterpart.
    Tristate signals (iobuf) expand to three signals: <name>_i, <name>_o, <name>_t.
    All other signals use the bare signal name regardless of buffer type.
    """
    pass


def _generate_vhdl_ioring_inst(signal_table: SignalTable, top: str) -> str:
    """Generate the IO ring entity instantiation for a VHDL top-level architecture.

    Returns a string containing the IO ring instance with port connections
    mapping pad-facing top-level ports and internal signals to the IO ring ports.
    Signals with bypass: true are excluded.
    """
    inst = []
    inst.append(f"    {top}_io_i0 : entity work.{top}_io")
    inst.append("    -- generic map (")
    inst.append("    -- )")
    inst.append("    port map (")

    ioring_ports = []

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
    name_len = ((longest_name // 4) + 1) * 4

    # Now iterate the list of ports in the IO ring and format them with a 4 space
    # indent, followed by another 4 spaces, then the calculated max length rounded up,
    # then the same port name again inside parens, and a trailing comma, except on
    # the last port
    for index, name in enumerate(ioring_ports):
        if index == len(ioring_ports) - 1:
            suffix = ""
        else:
            suffix = ","
        inst.append(f"{'':<8}{name:<{name_len}}=> {name}{suffix}")

    # Now attach the trailing parenthesis on its own
    inst.append(f"{'':<4});")

    return "\n".join(inst)
