from dataclasses import dataclass


@dataclass
class MetaTable:
    title: str
    part: str

    def __init__(self, doc: dict):
        pass
