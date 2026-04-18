from dataclasses import dataclass
from typing import Any


@dataclass
class ConstraintsTable:
    cfgbvs: str
    config_voltage: float


def build_constraints_table(doc: dict[str, Any]) -> ConstraintsTable:
    constraints = doc["constraints"]
    return ConstraintsTable(constraints["cfgbvs"], constraints["config_voltage"])
