from .rw_element import RainwaveElement


class RainwaveElseElement(RainwaveElement):
    def handle_start(self) -> str:
        return "else {"

    def handle_end(self) -> str:
        return "}"
