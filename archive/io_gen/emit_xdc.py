from typing import Any, Iterable

from io_gen.models import PinRow, SingleEnded, DiffPair


def emit_xdc(pin_table: Iterable[PinRow]) -> None:
    """
    Main entry point for generating XDC constraints files.  Will eventually support adding headers, footers, block
    replacement, file IO, etc.

    """
    return None


def emit_xdc_constraints(pin_table: Iterable[PinRow]) -> list[str]:
    """
    Emits per-port pairs of XDC constraints based on entries in the pin table
    - Preserves input order
    - For differential pairs, emits 'p' followed by 'n'
    - Uses `comment.xdc` if present

    """

    # The intent here is to emit the XDC comment (if there is one) at the start of a block of bus signals.
    # To do that, we use a simple state machine while we iterate over the rows with these in mind
    #   - We treat every contiguous block of the same `name` as one group.
    #   - We start a new bus or group when row.name != current_name
    #   - Emit the group's XDC comment once on the first for that group
    #   - Since we don't allow buses to split in the YAML, the group ends when the name changes

    current_name = None

    out: list[str] = []
    for entry in pin_table:
        # Final sanity check here before we move forward
        entry.validate()

        lines: list[str] = []
        # Are we starting a new group?
        if entry.name != current_name:
            # Add an empty line between groups, if this is not the first
            # group of signals
            if current_name is not None:
                out.append("")

            current_name = entry.name
            # Does this group of signals have comments?
            if entry.comment.xdc:
                lines.append(f"# {entry.comment.xdc}")

        lines.extend(_emit_package_pin(entry))
        lines.extend(_emit_iostandard(entry))

        out.extend(lines)

    # And then add a blank line to the end of the output
    out.append("")

    return out


def _emit_package_pin(entry: PinRow) -> list[str]:
    """Returns one or two lines of PACKAGE_PIN constraints"""
    lines: list[str] = []

    # This should not be reachable
    assert isinstance(entry, SingleEnded) or isinstance(
        entry, DiffPair
    ), f"Pin entry {entry.name} must be either single-ended or a differential pair"

    if isinstance(entry, SingleEnded):
        if entry.bus:
            get_ports_str = _xdc_get_ports(f"{entry.name}_pad", entry.index)
        else:
            get_ports_str = _xdc_get_ports(f"{entry.name}_pad")
        lines.append(f"set_property PACKAGE_PIN {entry.pin} [{get_ports_str}]")
    else:
        if entry.bus:
            get_ports_str = _xdc_get_ports(f"{entry.name}_p", entry.index)
            lines.append(f"set_property PACKAGE_PIN {entry.p} [{get_ports_str}]")
            get_ports_str = _xdc_get_ports(f"{entry.name}_n", entry.index)
            lines.append(f"set_property PACKAGE_PIN {entry.n} [{get_ports_str}]")
        else:
            get_ports_str = _xdc_get_ports(f"{entry.name}_p")
            lines.append(f"set_property PACKAGE_PIN {entry.p} [{get_ports_str}]")
            get_ports_str = _xdc_get_ports(f"{entry.name}_n")
            lines.append(f"set_property PACKAGE_PIN {entry.n} [{get_ports_str}]")
    return lines


def _emit_iostandard(entry: PinRow) -> list[str]:
    """Returns one or two lines of IOSTANDARD constraints"""
    lines: list[str] = []

    # This should not be reachable
    assert isinstance(entry, SingleEnded) or isinstance(
        entry, DiffPair
    ), f"Pin entry {entry.name} must be either single-ended or a differential pair"

    if isinstance(entry, SingleEnded):
        if entry.bus:
            get_ports_str = _xdc_get_ports(f"{entry.name}_pad", entry.index)
        else:
            get_ports_str = _xdc_get_ports(f"{entry.name}_pad")
        lines.append(f"set_property IOSTANDARD {entry.iostandard} [{get_ports_str}]")
    else:
        if entry.bus:
            get_ports_str = _xdc_get_ports(f"{entry.name}_p", entry.index)
            lines.append(
                f"set_property IOSTANDARD {entry.iostandard} [{get_ports_str}]"
            )
            get_ports_str = _xdc_get_ports(f"{entry.name}_n", entry.index)
            lines.append(
                f"set_property IOSTANDARD {entry.iostandard} [{get_ports_str}]"
            )
        else:
            get_ports_str = _xdc_get_ports(f"{entry.name}_p")
            lines.append(
                f"set_property IOSTANDARD {entry.iostandard} [{get_ports_str}]"
            )
            get_ports_str = _xdc_get_ports(f"{entry.name}_n")
            lines.append(
                f"set_property IOSTANDARD {entry.iostandard} [{get_ports_str}]"
            )
    return lines


def _xdc_get_ports(name: str, index: int | None = None) -> str:
    """Returns the get_ports command for a given port and index"""
    port = f"{name}[{index}]" if index is not None else name
    return f"get_ports {{{port}}}"
