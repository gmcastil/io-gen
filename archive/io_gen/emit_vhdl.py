from typing import Any, Iterable

from io_gen.models.signal import SignalRow


def emit_vhdl_signals(sig_table: Iterable[SignalRow]) -> list[dict[str, str]]:
    """ """

    out: list[dict] = []
    for sig in sig_table:
        name = sig.name
        if sig.bus:
            sig_type = "std_logic_vector"
            sig_range = f"({sig.width - 1} downto 0)"
        else:
            sig_type = "std_logic"
            sig_range = None
        out.append(dict(name=name, type=sig_type, range=sig_range))

    return out
