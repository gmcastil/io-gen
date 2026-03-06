from dataclasses import dataclass

from typing import Union

StrOrList = Union[str, list[str]]


@dataclass(frozen=True)
class Comment:
    hdl: str | None = None
    xdc: str | None = None
