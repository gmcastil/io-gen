from typing import Any

from io_gen.tables import signal_is_differential, signal_is_scalar

# Set of tristate buffers that will require '_i', '_o', and '_t' in the signal
# block and IO ring instances
TRISTATE_BUFFERS = {"iobuf"}


def _get_signal_top_ports(sig: dict[str, Any]) -> list[dict]:
    """Language-agnostic list of ports for the top level RTL for a given signal"""

    port_base = {
        "direction": sig["direction"],
        "width": sig["width"],
        "is_bus": not signal_is_scalar(sig),
    }

    port_list = []
    if signal_is_differential(sig):
        port_list.append({**port_base, "name": f"{sig['name']}_p"})
        port_list.append({**port_base, "name": f"{sig['name']}_n"})
    else:
        port_list.append({**port_base, "name": f"{sig['name']}_pad"})

    return port_list


def _get_signal_nets(sig: dict[str, Any]) -> list[dict]:
    """Language-agnostic list of nets from the IO ring to fabric-facing logic for a given signal"""

    net_base = {
        "width": sig["width"],
        "is_bus": not signal_is_scalar(sig),
    }

    if sig["bypass"]:
        return []

    net_list = []
    if sig["buffer"] not in TRISTATE_BUFFERS:
        net_list.append({**net_base, "name": sig["name"]})
    else:
        net_list.append({**net_base, "name": f"{sig['name']}_i"})
        net_list.append({**net_base, "name": f"{sig['name']}_o"})
        net_list.append({**net_base, "name": f"{sig['name']}_t"})

    return net_list


def _get_signal_ioring_ports(sig: dict[str, Any]) -> list[dict]:
    """Language-agnostic list of ports for IO ring RTL for a given siganl"""

    port_base = {
        "direction": sig["direction"],
        "width": sig["width"],
        "is_bus": not signal_is_scalar(sig),
    }

    # No bypassed signals in the IO ring.
    if sig["bypass"]:
        return []

    port_list = []
    if signal_is_differential(sig):
        if sig["direction"] == "in":
            port_list.append({**port_base, "name": f"{sig['name']}_p"})
            port_list.append({**port_base, "name": f"{sig['name']}_n"})
            port_list.append({**port_base, "name": sig["name"], "direction": "out"})
        elif sig["direction"] == "out":
            port_list.append({**port_base, "name": f"{sig['name']}_p"})
            port_list.append({**port_base, "name": f"{sig['name']}_n"})
            port_list.append({**port_base, "name": sig["name"], "direction": "in"})
        else:
            port_list.append({**port_base, "name": f"{sig['name']}_p"})
            port_list.append({**port_base, "name": f"{sig['name']}_n"})
            port_list.append(
                {**port_base, "name": f"{sig['name']}_i", "direction": "out"}
            )
            port_list.append(
                {**port_base, "name": f"{sig['name']}_o", "direction": "in"}
            )
            port_list.append(
                {**port_base, "name": f"{sig['name']}_t", "direction": "in"}
            )
    else:
        if sig["direction"] == "in":
            port_list.append({**port_base, "name": f"{sig['name']}_pad"})
            port_list.append({**port_base, "name": sig["name"], "direction": "out"})
        elif sig["direction"] == "out":
            port_list.append({**port_base, "name": f"{sig['name']}_pad"})
            port_list.append({**port_base, "name": sig["name"], "direction": "in"})
        else:
            port_list.append({**port_base, "name": f"{sig['name']}_pad"})
            port_list.append(
                {**port_base, "name": f"{sig['name']}_i", "direction": "out"}
            )
            port_list.append(
                {**port_base, "name": f"{sig['name']}_o", "direction": "in"}
            )
            port_list.append(
                {**port_base, "name": f"{sig['name']}_t", "direction": "in"}
            )

    return port_list


# def _build_top_port_list(signal_table: SignalTable) -> list[dict]:
#     """Language-agnostic list of all ports in the top level RTL

#     This is intended to be a heler function that returns the external ports for the top level RTL module. It returns
#     the signal name, direction, and type to attach '_pad' for single-ended signals and '_n' and '_p' for differential
#     signals. It also returns
#     """


# def _build_ioring_port_list(signal_table: SignalTable) -> list[dict]:
#     """Language-agnostic list of all ports in an IO ring

#     Ths is intended to be a helper function that returns the pad and fabric facing ports for the IO ring. It uses
#     the signal name, direction, and type to attach '_pad' for single-ended signals and '_n' and '_p' for differential
#     signals.  Signals with their direction as 'inout' follow an '_i', '_o', and '_t' pattern for fabric facing signals.

#     """

#     port_list: list[dict] = []
#     for sig in signal_table:
#         # Skipping bypassed signals entirely
#         if sig["bypass"]:
#             continue

#         # These are the same for every entry
#         width = sig["width"]
#         is_bus = False if signal_is_scalar(sig) else True

#         # Do diff pairs first
#         if signal_is_differential(sig):
#             # Signal is an input to the chip
#             if sig["direction"] == "in":
#                 # Do the pads first
#                 entry = {
#                     "name": f"{sig['name']}_p",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 # Differential n
#                 entry = {
#                     "name": f"{sig['name']}_n",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 # Now do the fabric facing side, which is an output in the IO ring
#                 entry = {
#                     "name": f"{sig['name']}",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#             # Signal is an output from the ship
#             elif sig["direction"] == "out":
#                 entry = {
#                     "name": f"{sig['name']}_p",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 entry = {
#                     "name": f"{sig['name']}_n",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 entry = {
#                     "name": f"{sig['name']}",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#             # Signal is an inout signal
#             else:
#                 entry = {
#                     "name": f"{sig['name']}_p",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 entry = {
#                     "name": f"{sig['name']}_n",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 # This is the tricky case where the directions will boggle your mind. These are defined from the
#                 # perspective of user logic.  So, the _i signal is an off chip input signal, but after teh buffer,
#                 # it becomes an output from the IO ring
#                 entry = {
#                     "name": f"{sig['name']}_i",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 # Similarly, the _o signal is an output from the chip, so its an input to the IO ring
#                 port_list.append(entry)
#                 entry = {
#                     "name": f"{sig['name']}_o",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 entry = {
#                     "name": f"{sig['name']}_t",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#         # Single ended signals now
#         else:
#             # Signal is an input to the chip
#             if sig["direction"] == "in":
#                 # Do the pad first
#                 entry = {
#                     "name": f"{sig['name']}_pad",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 # Now do the fabric facing side, which is an output in the IO ring
#                 entry = {
#                     "name": f"{sig['name']}",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#             # Signal is an output from the chip
#             elif sig["direction"] == "out":
#                 entry = {
#                     "name": f"{sig['name']}_pad",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 # Now do the fabric facing side, which is an output in the IO ring
#                 entry = {
#                     "name": f"{sig['name']}",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#             # Signal is an inout signal
#             else:
#                 entry = {
#                     "name": f"{sig['name']}_pad",
#                     "direction": "inout",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 # This is the tricky case where the directions will boggle your mind. These are defined from the
#                 # perspective of user logic.  So, the _i signal is an off chip input signal, but after teh buffer,
#                 # it becomes an output from the IO ring
#                 entry = {
#                     "name": f"{sig['name']}_i",
#                     "direction": "out",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 # Similarly, the _o signal is an output from the chip, so its an input to the IO ring
#                 port_list.append(entry)
#                 entry = {
#                     "name": f"{sig['name']}_o",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)
#                 entry = {
#                     "name": f"{sig['name']}_t",
#                     "direction": "in",
#                     "width": width,
#                     "is_bus": is_bus,
#                 }
#                 port_list.append(entry)

#     return port_list
