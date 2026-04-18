import re
from pathlib import Path

from .exceptions import ValidationError


# Pair supported buffers with their directions
BUFFER_DIRECTIONS = {
    "ibuf": "in",
    "obuf": "out",
    "ibufds": "in",
    "obufds": "out",
    "iobuf": "inout",
    "iobufds": "inout",
}

# Pair buffer with whether they are single or differential
BUFFER_STRATEGIES = {
    "ibuf": "pins",
    "obuf": "pins",
    "ibufds": "pinset",
    "obufds": "pinset",
    "iobuf": "pins",
    "iobufds": "pinset",
}

# Inference only supported for certain buffer types
BUFFER_INFERABLE = ["ibuf", "obuf"]


def _get_pin_names_from_signal(sig: dict) -> list[str]:
    """Get a list of all pins used by a signal"""
    pins: list[str] = []
    # Single-ended signal
    if "pins" in sig:
        if isinstance(sig["pins"], str):
            pins = [sig["pins"]]
        else:
            pins = sig["pins"]
    # Differential pair
    else:
        if isinstance(sig["pinset"]["p"], str):
            pin_p = sig["pinset"]["p"]
            pin_n = sig["pinset"]["n"]
            pins = [pin_p, pin_n]
        else:
            pins = sig["pinset"]["p"] + sig["pinset"]["n"]

    return pins


def _check_pin_name_format(signals: list[dict]) -> None:
    """Check that every pin name in the design contains only uppercase letters and digits.

    Validates all pin names across all signals, including both legs of pinset and
    signals with generate: false. Rejects anything containing whitespace, commas,
    brackets, lowercase letters, or any other non-alphanumeric characters. Also requires
    that the package pin is at least two characters in length

    Raises ValidationError identifying the first malformed pin name found.
    """
    pattern = re.compile(r"^[A-Z]+[0-9]+$")
    for sig in signals:
        name = sig["name"]
        pins = _get_pin_names_from_signal(sig)
        for pin in pins:
            if not pattern.match(pin):
                raise ValidationError(f"signal '{name}' has pin '{pin}': is malformed")


def _check_unique_signal_names(signals: list[dict]) -> None:
    """Check that no two signals share the same name.

    Raises ValidationError identifying the first duplicate name found.
    Applies to all signals, including those with generate: false.
    """
    uniq_names = set()
    for sig in signals:
        name = sig["name"]
        if name in uniq_names:
            raise ValidationError(f"signal '{name}': duplicate names")
        uniq_names.add(name)


def _check_unique_pins(signals: list[dict]) -> None:
    """Check that no physical pin is assigned to more than one signal.

    Checks both pins (scalar and array) and pinset (p and n legs).
    Applies to all signals, including those with generate: false.
    Raises ValidationError identifying the first duplicate pin found.
    """
    pins = set()
    for sig in signals:
        for pin in _get_pin_names_from_signal(sig):
            if pin in pins:
                raise ValidationError(f"Pin '{pin}': duplicate pins")
            pins.add(pin)


def _check_pinset_array_mismatch(sig: dict) -> None:
    """Check that pinset.p and pinset.n are the same type and length.

    Both must be scalar strings or both must be arrays. If arrays,
    they must have equal length.
    Raises ValidationError identifying the signal and the mismatch.
    Skips signals that do not use pinset.
    """
    if "pinset" in sig:
        name = sig["name"]
        p_pins = sig["pinset"]["p"]
        n_pins = sig["pinset"]["n"]

        if isinstance(p_pins, str) and isinstance(n_pins, str):
            return
        elif isinstance(p_pins, list) and isinstance(n_pins, list):
            if len(p_pins) != len(n_pins):
                raise ValidationError(f"signal '{name}': pinset array mismatch")
        else:
            raise ValidationError(f"signal '{name}': pinset type mismatch")


def _check_pins_array_width_match(sig: dict) -> None:
    """Check that the declared width matches the length of the pins array.

    Only applies when pins is an array. Raises ValidationError identifying
    the signal, the declared width, and the actual pin count.
    Skips signals that use scalar pins, pinset, or generate: false.
    """
    if "pins" in sig:
        name = sig["name"]
        pins = sig["pins"]
        if isinstance(pins, str):
            return
        elif isinstance(pins, list):
            # Recall, from the schema that width is only required for arrays
            width = sig["width"]
            if len(pins) != width:
                raise ValidationError(f"signal '{name}': pins array width mismatch")


def _check_pinset_array_width_match(sig: dict) -> None:
    """Check that the declared width matches the length of the pinset.p array.

    Only applies when pinset.p is an array. Raises ValidationError identifying
    the signal, the declared width, and the actual pin count.
    Skips signals that use scalar pinset, pins, or generate: false.
    """

    if "pinset" in sig:
        name = sig["name"]
        p_pins = sig["pinset"]["p"]
        n_pins = sig["pinset"]["n"]

        if isinstance(p_pins, str) and isinstance(n_pins, str):
            return
        elif isinstance(p_pins, list) and isinstance(n_pins, list):
            # Recall, from the schema that width is only required for arrays
            width = sig["width"]
            if len(p_pins) != width:
                raise ValidationError(f"signal '{name}': pinset array width mismatch")
            elif len(n_pins) != width:
                raise ValidationError(f"signal '{name}': pinset array width mismatch")


def _check_buffer_direction(sig: dict) -> None:
    """Check that the buffer type is compatible with the declared direction.

    Required pairings: ibuf->in, obuf->out, ibufds->in, obufds->out, iobuf->inout,
    iobufds->inout. Raises ValidationError identifying the signal, buffer, and direction.
    Skips signals with generate: false or bypass: true (no buffer required).
    """
    if not sig.get("generate", True) or sig.get("bypass", False):
        return

    name = sig["name"]
    buffer = sig["buffer"]
    direction = sig["direction"]

    if BUFFER_DIRECTIONS[buffer] != direction:
        raise ValidationError(
            f"signal '{name}': buffer {buffer} direction is {direction}"
        )


def _check_buffer_strategy_match(sig: dict) -> None:
    """Check that the buffer type is compatible with the pin assignment strategy.

    ibuf, obuf, and iobuf require pins. ibufds and obufds require pinset.
    Raises ValidationError identifying the signal, buffer, and pin strategy used.
    Skips signals with generate: false or bypass: true (no buffer required).
    """

    if not sig.get("generate", True) or sig.get("bypass", False):
        return

    name = sig["name"]
    buffer = sig["buffer"]
    if "pins" in sig:
        strategy = "pins"
    else:
        strategy = "pinset"

    if BUFFER_STRATEGIES[buffer] != strategy:
        raise ValidationError(
            f"signal '{name}': buffer {buffer} incompatible with '{strategy}'"
        )


def _check_buffer_infer_bypass_mismatch(sig: dict) -> None:
    """Check that bypass: true and infer: true are not both set on the same signal.

    These are mutually exclusive: bypass means an external component provides
    the buffer, while infer asks the synthesis tool to infer one.
    Raises ValidationError identifying the signal.
    """
    name = sig["name"]
    if sig.get("bypass", False) and sig.get("infer", False):
        raise ValidationError(
            f"signal '{name}': cannot infer buffer and bypass IO ring"
        )


def _check_buffer_inferable(sig: dict) -> None:
    """Check that infer: true is only used with ibuf or obuf.

    Synthesis inference is predictable and guaranteed correct only for these
    two single-ended buffer types. All other types must be instantiated explicitly.
    Raises ValidationError identifying the signal and buffer type.
    Skips signals where infer is false or not set.
    """
    if not sig.get("infer", False):
        return

    name = sig["name"]
    buffer = sig["buffer"]
    if buffer not in BUFFER_INFERABLE:
        raise ValidationError(f"signal '{name}': buffer {buffer} not inferable")


def _check_minimum_ports_generated(signals: list[dict]) -> None:
    """Check that at least one signal has generate: true.

    Raises ValidationError if all signals have generate: false, which would
    produce no usable output.
    """
    for sig in signals:
        status = sig.get("generate", True)
        if status:
            return
    raise ValidationError("no signals with generate: true - nothing to generate")


def _check_non_ascii(path: Path) -> None:
    """Checks a file to verify there are no non-ASCII characters present

    Raises ValidationError identifying the location of the first non-ASCII character
    in the provided path.
    """
    with open(path, "r", encoding="utf-8") as lines:
        for index, line in enumerate(lines, 1):
            if not line.isascii():
                raise ValidationError(f"found non-ASCII encoded string at line {index}")
