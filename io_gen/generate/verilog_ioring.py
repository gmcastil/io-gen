from typing import Any

from io_gen.tables import SignalTable
from io_gen.tables import PinTable

from .formatting import _indent_join


def generate_verilog_ioring(signal_table: SignalTable, pin_table: PinTable) -> str:
    pass


def _generate_verilog_ioring_ports(signal_table: SignalTable) -> str:
    pass


def _generate_verilog_ioring_body(
    signal_table: SignalTable, pin_table: PinTable
) -> str:
    return ""


def _infer_ibuf(name: str) -> str:
    """Infer an IBUF primitive"""
    return f"{'':<4}assign {name} = {name}_pad;"


def _infer_obuf(name: str) -> str:
    """Infer an OBUF primitive"""
    return f"{'':<4}assign {name}_pad = {name};"


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
    """Instantiate an IOBUF"""
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
