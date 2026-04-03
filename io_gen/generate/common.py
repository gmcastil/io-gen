from io_gen.tables import SignalTable
from io_gen.tables import signal_is_differential, signal_is_scalar
from io_gen.tables import PinTable


def _build_ioring_port_list(signal_table: SignalTable) -> list[dict]:
    """Language-agnostic list of all ports in an IO ring

    Ths is intended to be a helper function that returns the pad and fabric facing ports for the IO ring. It uses
    the signal name, direction, and type to attach '_pad' for single-ended signals and '_n' and '_p' for differential
    signals.  Signals with their direction as 'inout' follow an '_i', '_o', and '_t' pattern for fabric facing signals.

    """

    port_list: list[dict] = []
    for sig in signal_table:
        # Skipping bypassed signals entirely
        if sig["bypass"]:
            continue

        # These are the same for every entry
        width = sig["width"]
        is_bus = False if signal_is_scalar(sig) else True

        # Do diff pairs first
        if signal_is_differential(sig):
            # Signal is an input to the chip
            if sig["direction"] == "in":
                # Do the pads first
                entry = {
                    "name": f"{sig['name']}_p",
                    "direction": "in",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
                # Differential n
                entry = {
                    "name": f"{sig['name']}_n",
                    "direction": "in",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
                # Now do the fabric facing side, which is an output in the IO ring
                entry = {
                    "name": f"{sig['name']}",
                    "direction": "out",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
            # Signal is an output from the ship
            elif sig["direction"] == "out":
                entry = {
                    "name": f"{sig['name']}_p",
                    "direction": "out",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
                entry = {
                    "name": f"{sig['name']}_n",
                    "direction": "out",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
                entry = {
                    "name": f"{sig['name']}",
                    "direction": "in",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
            # Signal is an inout signal
            else:
                entry = {
                    "name": f"{sig['name']}_p",
                    "direction": "out",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
                entry = {
                    "name": f"{sig['name']}_n",
                    "direction": "out",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
                # This is the tricky case where the directions will boggle your mind. These are defined from the
                # perspective of user logic.  So, the _i signal is an off chip input signal, but after teh buffer,
                # it becomes an output from the IO ring
                entry = {
                    "name": f"{sig['name']}_i",
                    "direction": "out",
                    "width": width,
                    "is_bus": is_bus,
                }
                # Similarly, the _o signal is an output from the chip, so its an input to the IO ring
                port_list.append(entry)
                entry = {
                    "name": f"{sig['name']}_o",
                    "direction": "in",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
                entry = {
                    "name": f"{sig['name']}_t",
                    "direction": "in",
                    "width": width,
                    "is_bus": is_bus,
                }
                port_list.append(entry)
