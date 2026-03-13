from .exceptions import ValidationError


# raise ValidationError(f"signal '{name}': length mismatch")


def _get_pins_names_from_signal(sig: dict) -> list[str]:
    """Get a list of pins used by a signal"""
    pins: list[str] = []
    # Single-ended signal
    if "pins" in sig:
        if isinstance(sig["pins"], str):
            pin = sig["pins"]
            pins = [pin]
        else:
            pins = [pin for pin in sig["pins"]]
    # Differential pair
    else:
        if isinstance(sig["pinset"]["p"], str):
            pin_p = sig["pinset"]["p"]
            pin_n = sig["pinset"]["n"]
            pins = [pin_p, pin_n]
        else:
            pins = list(sig["pinset"]["p"])
            pins.extend(sig["pinset"]["n"])

    return pins


def _check_pin_name_format(signals: list[dict]) -> None:
    """Check that every pin name in the design contains only uppercase letters and digits.

    Validates all pin names across all signals, including both legs of pinset and
    signals with generate: false. Rejects anything containing whitespace, commas,
    brackets, lowercase letters, or any other non-alphanumeric characters.
    The required pattern is ^[A-Z0-9]+$.
    Raises ValidationError identifying the first malformed pin name found.
    """
    raise NotImplementedError


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
    uniq_pins = set()
    pins = list()
    # Get all of the pins of every signal in the design
    for sig in signals:
        pins.extend(_get_pins_names_from_signal(sig))
    # Iterate and check for duplicates
    for pin in pins:
        if pin in uniq_pins:
            raise ValidationError(f"Pin '{pin}': duplicate pins")
        else:
            uniq_pins.add(pin)


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
            raise ValidationError(f"signal '{name}': pinset p and n must be the same type")


def _check_pins_array_width_match(sig: dict) -> None:
    """Check that the declared width matches the length of the pins array.

    Only applies when pins is an array. Raises ValidationError identifying
    the signal, the declared width, and the actual pin count.
    Skips signals that use scalar pins, pinset, or generate: false.
    """
    raise NotImplementedError


def _check_pinset_array_width_match(sig: dict) -> None:
    """Check that the declared width matches the length of the pinset.p array.

    Only applies when pinset.p is an array. Raises ValidationError identifying
    the signal, the declared width, and the actual pin count.
    Skips signals that use scalar pinset, pins, or generate: false.
    """
    raise NotImplementedError


def _check_buffer_direction(sig: dict) -> None:
    """Check that the buffer type is compatible with the declared direction.

    Required pairings: ibuf->in, obuf->out, ibufds->in, obufds->out, iobuf->inout.
    Raises ValidationError identifying the signal, buffer, and direction.
    Skips signals with generate: false or bypass: true (no buffer required).
    """
    raise NotImplementedError


def _check_buffer_strategy_match(sig: dict) -> None:
    """Check that the buffer type is compatible with the pin assignment strategy.

    ibuf, obuf, and iobuf require pins. ibufds and obufds require pinset.
    Raises ValidationError identifying the signal, buffer, and pin strategy used.
    Skips signals with generate: false or bypass: true (no buffer required).
    """
    raise NotImplementedError


def _check_buffer_infer_bypass_mismatch(sig: dict) -> None:
    """Check that bypass: true and infer: true are not both set on the same signal.

    These are mutually exclusive: bypass means an external component provides
    the buffer, while infer asks the synthesis tool to infer one.
    Raises ValidationError identifying the signal.
    """
    raise NotImplementedError


def _check_buffer_inferable(sig: dict) -> None:
    """Check that infer: true is only used with ibuf or obuf.

    Synthesis inference is predictable and guaranteed correct only for these
    two single-ended buffer types. All other types must be instantiated explicitly.
    Raises ValidationError identifying the signal and buffer type.
    Skips signals where infer is false or not set.
    """
    raise NotImplementedError