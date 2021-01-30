from .rw_if_element import RainwaveIfElement


class RainwaveElsifElement(RainwaveIfElement):
    def handle_start(self) -> str:
        if_start = super().handle_start()
        return f"else {if_start}"
