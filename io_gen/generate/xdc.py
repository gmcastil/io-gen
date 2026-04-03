from io_gen.tables import PinTable
from io_gen.tables import SignalTable


def generate_xdc(signal_table: SignalTable, pin_table: PinTable) -> str:
    """Generate XDC constraints from the signal and pin tables"""
    result = []
    for sig in signal_table:
        name = sig["name"]
        comment = sig["comment"].get("xdc", None)

        # Constraints start with the XDC comment if present
        if comment:
            result.append(f"# {comment}")

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
                    result.append(pin_xdc)
                    result.append(iostandard_xdc)
                    # The n side
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin_n} [get_ports {{{name}_n[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_n[{index}]}}]"
                    result.append(pin_xdc)
                    result.append(iostandard_xdc)
                else:
                    # The p side
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin_p} [get_ports {name}_p]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_p]"
                    )
                    result.append(pin_xdc)
                    result.append(iostandard_xdc)
                    # The n side
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin_n} [get_ports {name}_n]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_n]"
                    )
                    result.append(pin_xdc)
                    result.append(iostandard_xdc)

            # Single-ended here
            else:
                pkg_pin = pin["pin"]
                iostandard = pin["iostandard"]
                index = pin["index"]

                if pin["is_bus"]:
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin} [get_ports {{{name}_pad[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_pad[{index}]}}]"
                    result.append(pin_xdc)
                    result.append(iostandard_xdc)
                else:
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin} [get_ports {name}_pad]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_pad]"
                    )
                    result.append(pin_xdc)
                    result.append(iostandard_xdc)

        # End of a signal's pins so we add a separator
        result.append("")

    return "\n".join(result) + "\n"
