from .rw_element import RainwaveElement


class RainwaveIfElement(RainwaveElement):
    def get_if_clause(self) -> str:
        attrs = self.attrs

        not_attr = next((attr for attr in attrs if attr[0] == "not"), None)
        left = next((attr for attr in attrs if attr[0] == "left"), None)
        op = next((attr for attr in attrs if attr[0] == "op"), None)
        right = next((attr for attr in attrs if attr[0] == "right"), None)

        if not left:
            raise Exception(f"if with no left")

        result = "("
        if not_attr:
            result += "!("
        left_value = left[1]
        result += f"{left_value}"
        if op and right:
            right_value = right[1]
            result += f" {op} {right_value}"
        elif (not op and right) or (op and not right):
            raise Exception(f"invalid if")
        result += ")"
        if not_attr:
            result += ")"

        return result

    def handle_start(self) -> str:
        if_clause = self.get_if_clause()
        return f"if {if_clause} {{"

    def handle_end(self) -> str:
        return "}"
