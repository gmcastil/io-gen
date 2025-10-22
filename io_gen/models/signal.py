from dataclasses import dataclass, field

from typing import Optional, Union

from .common import Comment


@dataclass(frozen=True)
class SignalRow:
    name: str
    group: Optional[str]
    direction: str
    buffer: str
    diff_pair: bool
    bus: bool
    width: int
    iostandard: str
    comment: Comment
