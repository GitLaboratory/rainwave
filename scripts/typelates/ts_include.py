import typing


class TSInclude:
    default_import_name: str or None
    named_imports: typing.Set[str]
    location: str

    def __init__(self, location: str) -> None:
        self.default_import_name = None
        self.named_imports = set()
        self.location = location

    def ts(self) -> str:
        buffer = "import "
        if self.default_import_name:
            buffer += self.default_import_name
            if self.named_imports:
                buffer += ", "
        if self.named_imports:
            buffer += "{"
            buffer += ",".join(self.named_imports)
            buffer += "}"
        buffer += f" from '{self.location}';"
        return buffer
