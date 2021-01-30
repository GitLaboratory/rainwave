from .rw_element import RainwaveElement


class RainwaveIfElement(RainwaveElement):
    def get_if_clause(self) -> str:
        attrs = self.attrs

        condition = next((attr for attr in attrs if attr[0] == "condition"), None)

        if not condition:
            raise Exception(f"if with no condition")

        return f"({condition[1]})"

    def handle_start(self) -> str:
        if_clause = self.get_if_clause()
        return f"if {if_clause} {{"

    def handle_end(self) -> str:
        return "}"
