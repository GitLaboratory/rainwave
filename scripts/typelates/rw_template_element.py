from .get_template_type_name import get_template_type_name
from .rw_element import RainwaveElement
from .template_bind import TemplateBind


class RainwaveTemplateElement(RainwaveElement):
    def handle_start(self) -> str:
        self.templates.append(self.tag)
        subtemplate_context = next(
            (attr[1] for attr in self.attrs if attr[0] == "context"), "context"
        )
        bind_name = next(
            (attr[1] for attr in self.attrs if attr[0] == "bind"), self.tag
        )
        self.binds.append(
            TemplateBind(
                name=bind_name, ts_type=get_template_type_name(self.tag), uid=self.uid
            )
        )
        return f"{self.uid}={self.tag}({subtemplate_context}, {self.append_to_element_uid});"

    def handle_end(self) -> str:
        return ""
