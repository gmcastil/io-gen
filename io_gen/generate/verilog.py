from io_gen.tables import SignalTable
from io_gen.tables import PinTable

def generate_verilog_ports(signal_table: SignalTable) -> str:
    """Generates the port declarations for the top level Verilog"""

    # Going to extract all the different columns that go in the module definition,
    # and then iterate over the three of these together and join them together
    for sig in signal_table:

        if not sig["generate"]:
            continue

        direction = sig["direction"]

        if "pins" in sig and isinstance(sig["pins"], str):
            is_bus = False
        elif "pinset" in sig and isinstance(sig["pinset"]["p"], str):
            is_bus = False
        else:
            is_bus = True

        # Begin with four space indent
        port_row = "    "
        port_row += f"{direction}"
        # Now pad it out to 16
        port_row.rjust

        



def generate_verilog_wires(signal_table: SignalTable) -> str:
    pass

def generate_verilog_ioring(signal_table: SignalTable, pin_table: PinTable) -> str:
    pass

def generate_verilog_ioring_inst(signal_table: SignalTable) -> str:
    pass

def generate_verilog_top(signal_table: Signal
    pass
