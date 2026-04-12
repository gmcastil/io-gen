from dataclasses import dataclass


@dataclass
class MetaTable:
    title: str
    part: str
    architecture: str | None


def build_meta_table(doc: dict) -> MetaTable:
    # The architecture is optional and can't be enforced by the schema. This
    # is required for VHDL files and its presence is looked for by the validate_vhdl function
    arch = doc.get("architecture", None)
    return MetaTable(doc["title"], doc["part"], arch)
