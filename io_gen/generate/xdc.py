from io_gen.tables import PinTable, pin_is_differential
from io_gen.tables import SignalTable
from io_gen.tables import ConstraintsTable

from .common import get_header


def generate_xdc(
    signal_table: SignalTable, pin_table: PinTable, constraints_table: ConstraintsTable
) -> str:
    """Generate XDC constraints from the signal and pin tables"""

    # Start by writing out the header
    xdc_lines = []
    header = []
    for line in get_header():
        if line:
            header.append(f"# {line}")
        else:
            header.append("#")
    xdc_lines.append("\n".join(header))

    # Set general configuration and bank voltage constraints
    constraints = [
        f"set_property CONFIG_VOLTAGE {constraints_table.config_voltage} [current_design]",
        f"set_property CFGBVS {constraints_table.cfgbvs} [current_design]",
    ]
    xdc_lines.append("\n".join(constraints))

    # Now add the individual pin constraints
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
            iostandard = pin["iostandard"]
            direction = pin["direction"].upper()
            # Differential pairs here
            if pin_is_differential(pin):
                pkg_pin_p = pin["pinset"]["p"]
                pkg_pin_n = pin["pinset"]["n"]
                index = pin["index"]

                if pin["is_bus"]:
                    # The p side
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin_p} [get_ports {{{name}_p[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_p[{index}]}}]"
                    direction_xdc = f"set_property DIRECTION {direction} [get_ports {{{name}_p[{index}]}}]"
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    lines.append(direction_xdc)
                    # The n side
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin_n} [get_ports {{{name}_n[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_n[{index}]}}]"
                    direction_xdc = f"set_property DIRECTION {direction} [get_ports {{{name}_n[{index}]}}]"
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    lines.append(direction_xdc)
                else:
                    # The p side
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin_p} [get_ports {name}_p]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_p]"
                    )
                    direction_xdc = (
                        f"set_property DIRECTION {direction} [get_ports {name}_p]"
                    )
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    lines.append(direction_xdc)
                    # The n side
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin_n} [get_ports {name}_n]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_n]"
                    )
                    direction_xdc = (
                        f"set_property DIRECTION {direction} [get_ports {name}_n]"
                    )
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    lines.append(direction_xdc)

            # Single-ended here
            else:
                pkg_pin = pin["pin"]
                iostandard = pin["iostandard"]
                index = pin["index"]

                if pin["is_bus"]:
                    pin_xdc = f"set_property PACKAGE_PIN {pkg_pin} [get_ports {{{name}_pad[{index}]}}]"
                    iostandard_xdc = f"set_property IOSTANDARD {iostandard} [get_ports {{{name}_pad[{index}]}}]"
                    direction_xdc = f"set_property DIRECTION {direction} [get_ports {{{name}_pad[{index}]}}]"
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    lines.append(direction_xdc)
                else:
                    pin_xdc = (
                        f"set_property PACKAGE_PIN {pkg_pin} [get_ports {name}_pad]"
                    )
                    iostandard_xdc = (
                        f"set_property IOSTANDARD {iostandard} [get_ports {name}_pad]"
                    )
                    direction_xdc = (
                        f"set_property DIRECTION {direction} [get_ports {name}_pad]"
                    )
                    lines.append(pin_xdc)
                    lines.append(iostandard_xdc)
                    lines.append(direction_xdc)

        # This gives a block of pin constraints, with the comment at the top and no intervening
        # blank lines.
        xdc_lines.append("\n".join(lines))

    # Now join them with a blank line in between each block and fnish with a newline at the end
    return "\n\n".join(xdc_lines) + "\n"
