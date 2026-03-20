from io_gen.tables import SignalTable, signal_is_scalar, signal_is_differential
from io_gen.tables import PinTable

from .generate.formatting import _apply_indent_and_suffix


def generate_verilog_top(signal_table: SignalTable) -> str:
    pass


def _generate_verilog_ports(signal_table: SignalTable) -> str:

    ports = []
    for sig in signal_table:

        # Skip signals that aren't to be generated
        if not sig["generate"]:
            continue

        # The strategy here is to create the entire list of ports and comments without any indent, then once it's
        # finished, iterate the result, add commas at the end of all but the last one and indent everything along the
        # way (use the fact that comments start with # before indenting, and then add the commas).

        # HDL comments if present
        comment_str = sig["comment"].get("hdl", None)
        if comment_str:
            ports.append(f"# {comment_str}")

        # Port direction
        if sig["direction"] == "in":
            direction_str = "input".ljust(7)
        elif sig["direction"] == "out":
            direction_str = "output".ljust(7)
        else:
            direction_str = "inout".ljust(7)

        # Net type and width block
        if signal_is_scalar(sig):
            width_str = f"wire".ljust(12)
        else:
            width_str = f"wire [{sig['width'] - 1}:0]".ljust(12)

        # Port names (no commas in the string yet)
        if signal_is_differential(sig):
            port_name = f"{sig['name']}_p"
            ports.append(f"{direction_str}{width_str}{port_name}")
            port_name = f"{sig['name']}_n"
            ports.append(f"{direction_str}{width_str}{port_name}")
        else:
            port_name = f"{sig['name']}_pad"
            ports.append(f"{direction_str}{width_str}{port_name}")

    # Now indent and append commas to every line


def _generate_verilog_wires(signal_table: SignalTable) -> str:
    pass


def _generate_verilog_ioring_inst(signal_table: SignalTable) -> str:
    pass
