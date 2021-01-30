from .rw_element import RainwaveElement
from .template_bind import TemplateBind


class RainwaveHTMLElement(RainwaveElement):
    def handle_start(self) -> str:
        uid = self.uid
        tag = self.tag
        attrs = self.attrs

        buffer = ""

        if not any(attr[0] == "bind" for attr in attrs):
            buffer += "const "
        buffer += f"{uid}=document.createElement('{tag}');"
        for [attr, value] in attrs:
            if attr == "bind":
                tag_camelcase = tag[0].upper() + tag[1:]
                ts_type = f"HTML{tag_camelcase}Element"
                self.binds.append(TemplateBind(name=value, ts_type=ts_type, uid=uid))
            elif attr == "class":
                buffer += f"{uid}.className=`{value}`;"
            elif attr == "href":
                buffer += f"{uid}.href=`{value}`;"
            elif attr == "helper":
                self.helpers.append(value)
            else:
                buffer += f"{uid}.setAttribute('{attr}',`{value}`);"
        buffer += f"{self.append_to_element_uid}.appendChild({uid});"
        return buffer

    def handle_end(self) -> str:
        return ""

    @property
    def element_uid(self) -> str:
        return self.uid
