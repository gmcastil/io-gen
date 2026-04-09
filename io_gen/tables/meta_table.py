class MetaTable:
    def __init__(self, title: str, part: str) -> None:
        self.title = title
        self.part = part


def _build_meta_table(doc: dict) -> MetaTable:
    return MetaTable(doc["title"], doc["part"])
