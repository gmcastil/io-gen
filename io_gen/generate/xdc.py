from io_gen.tables import PinTable
from io_gen.tables import SignalTable


def generate_xdc(signal_table: SignalTable, pin_table: PinTable) -> str:
    """Generate XDC constraints from the signal and pin tables"""
    sig_pins = []
    for sig in signal_table:
        name = sig["name"]
        comment = sig["comment"].get("xdc", None)

        lines = []
        # Constraints start with the XDC comment if present
        if comment:
            lines.append(f"# {comment}")

        # Get the list of pins from the pin table by name
        pins = pin_table[name]
        assert isinstance(pins, list)

        for pin in pins:
            # Differential pairs here
            if "pinset" in pin:
                pkg_pin_p = pin["pinset"]["p"]
                pkg_pin_n = pin["pinset"]["n"]
                iostandard = pin["iostandard"]
                index = pin["index"]

                if pin["is_bus"]:
                    # The p side
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin_p} [get_ports {{{name}_p[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_p[{index}]}}]"
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    # The n side
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin_n} [get_ports {{{name}_n[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_n[{index}]}}]"
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                else:
                    # The p side
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin_p} [get_ports {name}_p]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_p]"
                    )
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    # The n side
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin_n} [get_ports {name}_n]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_n]"
                    )
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)

            # Single-ended here
            else:
                pkg_pin = pin["pin"]
                iostandard = pin["iostandard"]
                index = pin["index"]

                if pin["is_bus"]:
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin} [get_ports {{{name}_pad[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_pad[{index}]}}]"
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                else:
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin} [get_ports {name}_pad]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_pad]"
                    )
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)

        # This gives a block of pin constraints, with the comment at the top and no intervening
        # blank lines.
        sig_pins.append("\n".join(lines))

    return "\n\n".join(sig_pins) + "\n"
