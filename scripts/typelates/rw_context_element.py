import typing

from .rw_element import RainwaveElement


class RainwaveContextElement(RainwaveElement):
    buffer: str
    variables: typing.List[set]

    def handle_start(self) -> str:
        self.variables = []
        return ""

    def handle_end(self) -> str:
        self.buffer = "interface Context {"
        for (name, ts_type, rw_type) in self.variables:
            self.buffer += f"{name}: "
            if rw_type:
                interface_name = rw_type[0].upper() + rw_type[1:]
                self.types.append((interface_name, rw_type))
                self.buffer += interface_name
            else:
                self.buffer += ts_type
            self.buffer += ";"
        self.buffer += "}\n\n"
        return ""

    def add_var(self, attrs) -> str:
        name = next(attr[1] for attr in attrs if attr[0] == "name")
        ts_type = next((attr[1] for attr in attrs if attr[0] == "tstype"), None)
        rw_type = next((attr[1] for attr in attrs if attr[0] == "rwtype"), None)
        if not ts_type and not rw_type:
            raise Exception(f"{self} has neither tstype or rwtype.")
        self.variables.append((name, ts_type, rw_type))


class RainwaveVarElement(RainwaveElement):
    def handle_start(self):
        return ""

    def handle_end(self):
        return ""

