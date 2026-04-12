from dataclasses import dataclass


@dataclass
class ConstraintsTable:
    cfgbvs: str
    config_voltage: float


def build_constraints_table(doc: dict) -> ConstraintsTable:
    constraints = doc["constraints"]
    return ConstraintsTable(constraints["cfgbvs"], constraints["config_voltage"])
