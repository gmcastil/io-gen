from typing import Any

from io_gen.tables import SignalTable
from io_gen.tables import PinTable

from .formatting import _indent_join
from .common import _get_ioring_header, _get_signal_ioring_ports


def generate_vhdl_ioring(
    signal_table: SignalTable, pin_table: PinTable, top: str, arch: str
) -> str:
    """Generate the complete VHDL IO ring entity and architecture as a string.

    Assembles the library clauses, entity declaration, port list, inferred and
    instantiated buffers by calling private helpers in order.
    """
    pass


def _generate_vhdl_ioring_ports(signal_table: SignalTable) -> str:
    """Generate the indented port declaration list for the IO ring in VHDL."""
    pass


def _generate_vhdl_ioring_body(
    signal_table: SignalTable, pin_table: PinTable
) -> str:
    """Generate the buffer instantiation body for the VHDL IO ring architecture."""
    pass


def _infer_ibuf(name: str) -> str:
    """Infer an IBUF primitive - connect fabric signal from pad port via assignment."""
    pass


def _infer_obuf(name: str) -> str:
    """Infer an OBUF primitive - connect pad port from fabric signal via assignment."""
    pass


def _instantiate_ibuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IBUF."""
    pass


def _instantiate_obuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an OBUF."""
    pass


def _instantiate_ibufds(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IBUFDS."""
    pass


def _instantiate_obufds(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an OBUFDS."""
    pass


def _instantiate_iobuf(name: str, pin_row: dict[str, Any]) -> str:
    """Instantiate an IOBUF."""
    pass


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
