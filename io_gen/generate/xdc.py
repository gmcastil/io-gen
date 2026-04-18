from io_gen.tables import PinTable, pin_is_differential
from io_gen.tables import SignalTable
from io_gen.tables import ConstraintsTable

from .common import get_header


def _port_ref(name: str, suffix: str, index: int, is_bus: bool) -> str:
    """Returns the port reference - buses get curly braces, scalars don't"""
    if is_bus:
        return f"{{{name}_{suffix}[{index}]}}"
    return f"{name}_{suffix}"


def _pin_constraints(
    pkg_pin: str, port: str, pin: dict, pin_planner: bool
) -> list[str]:
    """Returns the pin constraints for a port"""
    lines = [
        f"set_property PACKAGE_PIN {pkg_pin} [get_ports {port}]",
        f"set_property IOSTANDARD {pin['iostandard']} [get_ports {port}]",
    ]
    if pin_planner:
        lines.append(
            f"set_property DIRECTION {pin['direction'].upper()} [get_ports {port}]"
        )
    return lines


def generate_xdc(
    signal_table: SignalTable,
    pin_table: PinTable,
    constraints_table: ConstraintsTable,
    pin_planner: bool = False,
) -> str:
    """Generate XDC constraints from the signal and pin tables"""

    xdc_lines = []
    header = []
    for line in get_header():
        if line:
            header.append(f"# {line}")
        else:
            header.append("#")
    xdc_lines.append("\n".join(header))

    constraints = [
        f"set_property CONFIG_VOLTAGE {constraints_table.config_voltage} [current_design]",
        f"set_property CFGBVS {constraints_table.cfgbvs} [current_design]",
    ]
    xdc_lines.append("\n".join(constraints))

    for sig in signal_table:
        name = sig["name"]
        comment = sig["comment"].get("xdc", None)

        lines = []
        if comment:
            lines.append(f"# {comment}")

        for pin in pin_table[name]:
            index = pin["index"]
            is_bus = pin["is_bus"]
            if pin_is_differential(pin):
                port_ref = _port_ref(name, "p", index, is_bus)
                lines.extend(
                    _pin_constraints(pin["pinset"]["p"], port_ref, pin, pin_planner)
                )
                port_ref = _port_ref(name, "n", index, is_bus)
                lines.extend(
                    _pin_constraints(pin["pinset"]["n"], port_ref, pin, pin_planner)
                )
            else:
                port_ref = _port_ref(name, "pad", index, is_bus)
                lines.extend(_pin_constraints(pin["pin"], port_ref, pin, pin_planner))

        xdc_lines.append("\n".join(lines))

    return "\n\n".join(xdc_lines) + "\n"
