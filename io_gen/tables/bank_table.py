from dataclasses import dataclass


@dataclass
class Bank:
    iostandard: str
    performance: str


class BankTable:

    def __init__(self, doc: dict):
        pass
