from io_gen.tables import SignalTable
from io_gen.tables import PinTable

from .common import _build_ioring_port_list


def generate_verilog_ioring(signal_table: SignalTable, pin_table: PinTable) -> str:
    pass


def _generate_verilog_ioring_ports(signal_table: SignalTable) -> str:
    pass


def _generate_verilog_ioring_body(
    signal_table: SignalTable, pin_table: PinTable
) -> str:
    pass


def _build_ioring_port_list(signal_table: SignalTable) -> list[tuple]:
    """Returns the port list shape in a language independent fashion"""

    ports = []
    for sig in signal_table:
        if not sig["generate"] or not sig["bypass"]:
            continue

        width = sig["width"]
        name = sig["name"]
        direction = sig["disrection"]
