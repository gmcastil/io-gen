from typing import Any

from io_gen.tables import SignalTable
from io_gen.tables import PinTable

from .formatting import _indent_join
from .common import _get_ioring_header, _get_signal_ioring_ports, VLOG_DIRECTIONS


def generate_verilog_ioring(
    signal_table: SignalTable, pin_table: PinTable, top: str
) -> str:
    """Generate the complete Verilog IO ring as a string

    Assembles the module declaration, port list, inferred and instantiated buffers
    by calling private helpers in order.
    """

    rtl = []
    for line in _get_ioring_header():
        if line:
            rtl.append(f"// {line}")
        else:
            rtl.append(f"//")
    rtl.append(f"module {top}_io //#(")
    rtl.append(f"//)")
    rtl.append(f"(")
    rtl.append(_generate_verilog_ioring_ports(signal_table))
    rtl.append(f");")
    rtl.append(f"")
    rtl.append(_generate_verilog_ioring_body(signal_table, pin_table))
    rtl.append(f"")
    # Add a newline here so that the file ends appropriately
    rtl.append(f"endmodule\n")

    return "\n".join(rtl)


def _generate_verilog_ioring_ports(signal_table: SignalTable) -> str:
    """Generate the indented port declaration list for the IO ring in Verilog"""
    ports = []
    for sig in signal_table:
        # Skip ports that don't exist in the IO ring
        if sig["bypass"]:
            continue

        for port in _get_signal_ioring_ports(sig):
            direction = VLOG_DIRECTIONS[port["direction"]]
            if port["is_bus"]:
                width = f"[{port['width'] - 1}:0]"
            else:
                width = f""
            dim = f"wire {width}"
            line = f"{direction:<8}{dim:<16}{port['name']}"
            ports.append(line)

    return _indent_join(ports, 1, ",\n")


def _generate_verilog_ioring_body(
    signal_table: SignalTable, pin_table: PinTable
) -> str:
    """Generate the buffer instantiation body for the Verilog IO ring"""
    body = []
    for sig in signal_table:
        if sig["bypass"]:
            continue

        # Already checked during validation that this entire signal will be inferable, so
        # look up the function to call an call it
        if sig["infer"]:
            body.append(_INFER_BUFFERS[sig["buffer"]](sig["name"]))
        # Otherwise, for direct instantiation, we have to iterate the pins
        else:
            for pin_row in pin_table[sig["name"]]:
                body.append(_INSTANTIATE_BUFFERS[sig["buffer"]](sig["name"], pin_row))

    return _indent_join(body, 0, "\n\n")


def _infer_ibuf(name: str) -> str:
    """Infer an IBUF primitive"""
    return f"    assign {name} = {name}_pad;"


def _infer_obuf(name: str) -> str:
    """Infer an OBUF primitive"""
    return f"    assign {name}_pad = {name};"


def _instantiate_ibuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IBUF"""
    inst = []
    inst.append(f"IBUF //#(")
    inst.append(f"//)")
    inst.append(f"{pin_row['instance']} (")
    if pin_row["is_bus"]:
        inst.append(f"    .O  ({name}[{pin_row['index']}]),")
        inst.append(f"    .I  ({name}_pad[{pin_row['index']}])")
    else:
        inst.append(f"    .O  ({name}),")
        inst.append(f"    .I  ({name}_pad)")
    inst.append(f");")
    return _indent_join(inst, 1)


def _instantiate_obuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an OBUF"""
    inst = []
    inst.append(f"OBUF //#(")
    inst.append(f"//)")
    inst.append(f"{pin_row['instance']} (")
    if pin_row["is_bus"]:
        inst.append(f"    .O  ({name}_pad[{pin_row['index']}]),")
        inst.append(f"    .I  ({name}[{pin_row['index']}])")
    else:
        inst.append(f"    .O  ({name}_pad),")
        inst.append(f"    .I  ({name})")
    inst.append(f");")
    return _indent_join(inst, 1)


def _instantiate_ibufds(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IBUFDS"""
    inst = []
    inst.append(f"IBUFDS //#(")
    inst.append(f"//)")
    inst.append(f"{pin_row['instance']} (")
    if pin_row["is_bus"]:
        inst.append(f"    .O  ({name}[{pin_row['index']}]),")
        inst.append(f"    .I  ({name}_p[{pin_row['index']}]),")
        inst.append(f"    .IB ({name}_n[{pin_row['index']}])")
    else:
        inst.append(f"    .O  ({name}),")
        inst.append(f"    .I  ({name}_p),")
        inst.append(f"    .IB ({name}_n)")
    inst.append(f");")
    return _indent_join(inst, 1)


def _instantiate_obufds(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an OBUFDS"""
    inst = []
    inst.append(f"OBUFDS //#(")
    inst.append(f"//)")
    inst.append(f"{pin_row['instance']} (")
    if pin_row["is_bus"]:
        inst.append(f"    .O  ({name}_p[{pin_row['index']}]),")
        inst.append(f"    .OB ({name}_n[{pin_row['index']}]),")
        inst.append(f"    .I  ({name}[{pin_row['index']}])")
    else:
        inst.append(f"    .O  ({name}_p),")
        inst.append(f"    .OB ({name}_n),")
        inst.append(f"    .I  ({name})")
    inst.append(f");")
    return _indent_join(inst, 1)


def _instantiate_iobuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instatiate an IOBUF"""
    inst = []
    inst.append(f"IOBUF //#(")
    inst.append(f"//)")
    inst.append(f"{pin_row['instance']} (")
    if pin_row["is_bus"]:
        inst.append(f"    .O  ({name}_i[{pin_row['index']}]),")
        inst.append(f"    .I  ({name}_o[{pin_row['index']}]),")
        inst.append(f"    .IO ({name}_pad[{pin_row['index']}]),")
        inst.append(f"    .T  ({name}_t[{pin_row['index']}])")
    else:
        inst.append(f"    .O  ({name}_i),")
        inst.append(f"    .I  ({name}_o),")
        inst.append(f"    .IO ({name}_pad),")
        inst.append(f"    .T  ({name}_t)")
    inst.append(f");")
    return _indent_join(inst, 1)


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
