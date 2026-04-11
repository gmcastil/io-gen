from typing import Any

from io_gen.tables import SignalTable
from io_gen.tables import PinTable
from io_gen.tables import MetaTable

from .formatting import indent_join
from .common import get_ioring_header, get_signal_ioring_ports, VHDL_DIRECTIONS


def generate_vhdl_ioring(
    signal_table: SignalTable, pin_table: PinTable, meta_table: MetaTable, top: str
) -> str:
    """Generate the complete VHDL IO ring entity and architecture as a string.

    Assembles the library clauses, entity declaration, port list, inferred and
    instantiated buffers by calling private helpers in order.
    """
    arch = meta_table.architecture
    rtl = []
    for line in get_ioring_header():
        if line:
            rtl.append(f"-- {line}")
        else:
            rtl.append("--")
    rtl.append("library ieee;")
    rtl.append("use ieee.std_logic_1164.all;")
    rtl.append("")
    rtl.append("library unisim;")
    rtl.append("use unisim.vcomponents.all;")
    rtl.append("")
    rtl.append(f"entity {top}_io is")
    rtl.append("    -- generic (")
    rtl.append("    -- )")
    rtl.append("    port (")
    rtl.append(_generate_vhdl_ioring_ports(signal_table))
    rtl.append("    );")
    rtl.append(f"end entity {top}_io;")
    rtl.append("")
    rtl.append(f"architecture {arch} of {top}_io is")
    rtl.append("")
    rtl.append("begin")
    rtl.append("")
    rtl.append(_generate_vhdl_ioring_body(signal_table, pin_table))
    rtl.append("")
    rtl.append(f"end architecture {arch};\n")

    return "\n".join(rtl)


def _generate_vhdl_ioring_ports(signal_table: SignalTable) -> str:
    """Generate the indented port declaration list for the IO ring in VHDL."""
    port_names = []
    for sig in signal_table.active():
        for port in get_signal_ioring_ports(sig):
            port_names.append(port["name"])

    if not port_names:
        return ""

    longest_name = len(max(port_names, key=len))
    name_len = ((longest_name // 4) + 1) * 4

    all_ports = []
    for sig in signal_table.active():
        all_ports.extend(get_signal_ioring_ports(sig))

    ports = []
    for port_index, port in enumerate(all_ports):
        # Craft the string to go on the LHS of the colon
        lhs_line = f"{port['name']:<{name_len}}"

        # Create the string for the RHS of the colon
        direction = VHDL_DIRECTIONS[port["direction"]]
        if port["is_bus"]:
            rhs_line = f"{direction:<6}std_logic_vector({port['width'] - 1} downto 0)"
        else:
            rhs_line = f"{direction:<6}std_logic"

        # Append a semicolon to all but the last port in the port list
        if port_index != len(all_ports) - 1:
            rhs_line = f"{rhs_line};"

        # Assemble the actual line
        ports.append(f"{lhs_line}: {rhs_line}")

    return indent_join(ports, 2)


def _generate_vhdl_ioring_body(signal_table: SignalTable, pin_table: PinTable) -> str:
    """Generate the buffer instantiation body for the VHDL IO ring"""
    body = []
    for sig in signal_table.active():
        if sig["infer"]:
            body.append(_INFER_BUFFERS[sig["buffer"]](sig["name"]))
        else:
            for pin_row in pin_table[sig["name"]]:
                body.append(_INSTANTIATE_BUFFERS[sig["buffer"]](sig["name"], pin_row))

    return indent_join(body, 0, "\n\n")


def _infer_ibuf(name: str) -> str:
    """Infer an IBUF primitive"""
    return f"    {name} <= {name}_pad;"


def _infer_obuf(name: str) -> str:
    """Infer an OBUF primitive"""
    return f"    {name}_pad <= {name};"


def _instantiate_ibuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IBUF"""
    inst = []
    inst.append(f"{pin_row['instance']} : IBUF")
    inst.append("-- generic map (")
    inst.append("-- )")
    inst.append("port map (")
    if pin_row["is_bus"]:
        inst.append(f"    O   => {name}({pin_row['index']}),")
        inst.append(f"    I   => {name}_pad({pin_row['index']})")
    else:
        inst.append(f"    O   => {name},")
        inst.append(f"    I   => {name}_pad")
    inst.append(");")
    return indent_join(inst, 1)


def _instantiate_obuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an OBUF"""
    inst = []
    inst.append(f"{pin_row['instance']} : OBUF")
    inst.append("-- generic map (")
    inst.append("-- )")
    inst.append("port map (")
    if pin_row["is_bus"]:
        inst.append(f"    O   => {name}_pad({pin_row['index']}),")
        inst.append(f"    I   => {name}({pin_row['index']})")
    else:
        inst.append(f"    O   => {name}_pad,")
        inst.append(f"    I   => {name}")
    inst.append(");")
    return indent_join(inst, 1)


def _instantiate_ibufds(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IBUFDS."""
    inst = []
    inst.append(f"{pin_row['instance']} : IBUFDS")
    inst.append("-- generic map (")
    inst.append("-- )")
    inst.append("port map (")
    if pin_row["is_bus"]:
        inst.append(f"    O   => {name}({pin_row['index']}),")
        inst.append(f"    I   => {name}_p({pin_row['index']}),")
        inst.append(f"    IB  => {name}_n({pin_row['index']})")
    else:
        inst.append(f"    O   => {name},")
        inst.append(f"    I   => {name}_p,")
        inst.append(f"    IB  => {name}_n")
    inst.append(");")
    return indent_join(inst, 1)


def _instantiate_obufds(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an OBUFDS"""
    inst = []
    inst.append(f"{pin_row['instance']} : OBUFDS")
    inst.append("-- generic map (")
    inst.append("-- )")
    inst.append("port map (")
    if pin_row["is_bus"]:
        inst.append(f"    O   => {name}_p({pin_row['index']}),")
        inst.append(f"    OB  => {name}_n({pin_row['index']}),")
        inst.append(f"    I   => {name}({pin_row['index']})")
    else:
        inst.append(f"    O   => {name}_p,")
        inst.append(f"    OB  => {name}_n,")
        inst.append(f"    I   => {name}")
    inst.append(");")
    return indent_join(inst, 1)


def _instantiate_iobuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IOBUF"""
    inst = []
    inst.append(f"{pin_row['instance']} : IOBUF")
    inst.append("-- generic map (")
    inst.append("-- )")
    inst.append("port map (")
    if pin_row["is_bus"]:
        inst.append(f"    O   => {name}_i({pin_row['index']}),")
        inst.append(f"    I   => {name}_o({pin_row['index']}),")
        inst.append(f"    IO  => {name}_pad({pin_row['index']}),")
        inst.append(f"    T   => {name}_t({pin_row['index']})")
    else:
        inst.append(f"    O   => {name}_i,")
        inst.append(f"    I   => {name}_o,")
        inst.append(f"    IO  => {name}_pad,")
        inst.append(f"    T   => {name}_t")
    inst.append(");")
    return indent_join(inst, 1)


_INFER_BUFFERS = {
    "ibuf": _infer_ibuf,
    "obuf": _infer_obuf,
}

_INSTANTIATE_BUFFERS = {
    "ibuf": _instantiate_ibuf,
    "obuf": _instantiate_obuf,
    "ibufds": _instantiate_ibufds,
    "obufds": _instantiate_obufds,
    "iobuf": _instantiate_iobuf,
}
