import typing

from .template_bind import TemplateBind


class RainwaveElement:
    tag: str
    uid: str
    append_to_element_uid: str
    attrs: typing.List[set]
    binds: typing.List[TemplateBind]
    helpers: typing.List[str]
    templates: typing.List[str]
    types: typing.List[str]

    def __init__(
        self, tag: str, attrs: list, uid: str, append_to_element_uid: str
    ) -> None:
        self.tag = tag
        self.attrs = attrs
        self.uid = uid
        self.append_to_element_uid = append_to_element_uid

        self.binds = []
        self.helpers = []
        self.templates = []
        self.types = []

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} {self.tag} {self.attrs} {self.uid}>"

    def __repr__(self) -> str:
        return str(self)

    def handle_start(self) -> str:
        raise NotImplementedError

    def handle_end(self) -> str:
        raise NotImplementedError

    @property
    def element_uid(self) -> str:
        return self.append_to_element_uid
