from dataclasses import dataclass


@dataclass(frozen=True)
class Comment:
    hdl: str | None = None
    xdc: str | None = None
