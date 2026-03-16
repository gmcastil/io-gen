from collections.abc import Iterator
from copy import deepcopy


class SignalTable:
    def __init__(self) -> None:
        self.table = list()

    def __iter__(self) -> Iterator[dict[str, object]]:
        return iter(self.table)

    def __len__(self) -> int:
        return len(self.table)

    def add(self, sig[dict[str, object]]) -> None:
        """Add a signal to the signal table, resolving fields as needed"""

        # Assert that the common fields exist first - name, pins or pinset, generate, and width
        assert "name" in sig
        assert "pins" in sig or "pinset" in sig
        # Assert the shape - doing this here as a way of documenting our expectations here
        if "pins" in sig:
            assert isinstance(sig["pins"], str) or isinstance(sig["pins"], list)
        elif "pinset" in sig:
            assert isinstance(sig["pinset"], dict)
            assert isinstance(sig["pinset"]["p"], str) or isinstance(sig["pinset"]["p"], list)
            assert isinstance(sig["pinset"]["n"], str) or isinstance(sig["pinset"]["n"], list)
        assert "generate" in sig

        row = dict()

        # The philospohy here is that we are building up our row entry, not just
        # reassigning what came out of the YAML. Start with the common stuff
        row["name"] = sig["name"]
        if "pins" in sig:
            if isinstance(sig["pins"], str):
                # Here, width isn't requied in the schema, so we insert it
                row["width"] = 1
                row["pins"] = sig["pins"]
            else:
                # Here, width actually is required, so we grab it directly
                row["width"] = sig["width"]
                # Shallow copying here as best practice
                row["pins"] = list(sig["pins"])
        else:
            if isinstance(sig["pinset"]["p"], str):
                row["width"] = 1
                row["pinset"] = deepcopy(sig["pinset"])
            else:
                row["width"] = sig["width"]
                row["pinset"] = deepcopy(sig["pinset"])

        row["generate"] = sig["generate"]


        
        # The largest differnet in objects added to the signal table are whether or not they
        # are intended to actually be generated, so we'll separate those out at first.
        



            # Do a shallow copy here
            row["pins"] = list(sig["pins"])
            if isinstance(sig["pins"], str):
                row["width"] = 1
            else:
                assert(isinstance(sig["pins"], list))
                row["width"] = len(sig["pins"])
        else:
            if 



        if not sig["generate"]:
            if pins

            


def build_signal_table(doc: dict) -> "SignalTable":
    raise NotImplementedError
