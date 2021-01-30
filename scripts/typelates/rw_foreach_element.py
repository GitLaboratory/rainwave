from .rw_element import RainwaveElement


class RainwaveForeachElement(RainwaveElement):
    def handle_start(self) -> str:
        attrs = self.attrs
        array_name = next(attr for attr in attrs if attr[0] == "array")[1]
        return f"{array_name}.forEach(context => {{"

    def handle_end(self) -> str:
        return "});"
