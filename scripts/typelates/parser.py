import typing
from html.parser import HTMLParser

from .rw_context_element import RainwaveContextElement, RainwaveVarElement
from .rw_element import RainwaveElement
from .rw_else_element import RainwaveElseElement
from .rw_elsif_element import RainwaveElsifElement
from .rw_foreach_element import RainwaveForeachElement
from .rw_html_element import RainwaveHTMLElement
from .rw_if_element import RainwaveIfElement
from .rw_template_element import RainwaveTemplateElement
from .template_bind import TemplateBind
from .ts_include import TSInclude

TAG_HANDLERS = {
    "if": RainwaveIfElement,
    "else": RainwaveElseElement,
    "elsif": RainwaveElsifElement,
    "context": RainwaveContextElement,
    "var": RainwaveVarElement,
    "foreach": RainwaveForeachElement,
}

UNIQUE_ID_CHARS = [chr(x) for x in range(65, 91)] + [chr(x) for x in range(97, 123)]


class RainwaveParser(HTMLParser):
    binds: typing.List[TemplateBind]
    buffer: str
    construct_tree: typing.List[RainwaveElement]
    context: RainwaveContextElement
    helper_runs: typing.List[str]
    available_helpers: typing.Dict[str, str]
    includes: typing.Dict[str, TSInclude]
    input_buffer: str
    interface_name: str
    name: str
    available_templates: typing.Dict[str, str]

    _current_unique_id: str

    def __init__(self, template_name: str, templates: dict, helpers: dict) -> None:
        super().__init__()

        self.binds = []
        self.buffer = ""
        self.construct_tree = []
        self.helper_runs = []
        self.available_helpers = helpers
        self.includes = {}
        self.input_buffer = ""
        self.interface_name = template_name[0].upper() + template_name[1:] + "Template"
        self.name = template_name
        self.available_templates = templates

        self._current_unique_id = UNIQUE_ID_CHARS[0]

    def get_next_uid(self) -> str:
        next_idx = UNIQUE_ID_CHARS.index(self._current_unique_id[-1]) + 1
        if next_idx >= len(UNIQUE_ID_CHARS):
            self._current_unique_id += UNIQUE_ID_CHARS[0]
        else:
            self._current_unique_id = (
                self._current_unique_id[:-1] + UNIQUE_ID_CHARS[next_idx]
            )
        return self._current_unique_id

    def add_helper(self, helper: str) -> None:
        if not helper in self.available_helpers:
            raise Exception(f"{self.name} called nonexistent helper {helper}")
        location = self.available_helpers[helper]
        self.includes.setdefault(location, TSInclude(location))
        self.includes[location].default_import_name = helper

    def add_template(self, template: str) -> None:
        if not template in self.available_templates:
            raise Exception(f"{self.name} called nonexistent template {template}")
        location = self.available_templates[template] + ".template"
        template_import = template[0].upper() + template[1:]
        self.includes.setdefault(location, TSInclude(location))
        self.includes[location].default_import_name = template
        self.includes[location].named_imports.add(f"{template_import}Template")

    @property
    def current_uid(self) -> str:
        if len(self.construct_tree) == 0:
            return "rootFragment"
        else:
            return self.construct_tree[-1].uid

    @property
    def current_element_uid(self) -> str:
        append_to_element_uid = "rootFragment"
        if len(self.construct_tree) > 0:
            append_to_element_uid = self.construct_tree[-1].element_uid
        return append_to_element_uid

    def close(self, *args, **kwargs) -> str:
        self.handle_data(None)

        super().close(*args, **kwargs)

        if len(self.construct_tree) > 0:
            stack = "\n".join(self.construct_tree)
            raise Exception(f"{self.name} unclosed stack: {stack}")

        pre_buffer = ""

        for include in self.includes.values():
            pre_buffer += include.ts()

        for (itype_name, itype) in self.context.types:
            import_location = itype[0].lower() + itype[1:]
            pre_buffer += f"import {itype_name} from 'types/{import_location}';"

        pre_buffer += f"\n\nexport interface {self.interface_name} {{"
        pre_buffer += "rootFragment: HTMLElement | DocumentFragment;"
        for bind in self.binds:
            pre_buffer += f"{bind.name}: {bind.ts_type}"
            if bind.inside_if:
                pre_buffer += " | undefined"
            pre_buffer += ";"

        pre_buffer += "}\n\n"

        pre_buffer += self.context.buffer

        pre_buffer += f"export default function {self.name} ("
        pre_buffer += r"  context: Context, "
        pre_buffer += r"  rootFragment: HTMLElement | DocumentFragment = document.createDocumentFragment()"
        pre_buffer += f"): {self.interface_name} {{"

        for bind in self.binds:
            pre_buffer += f"let {bind.uid}: {bind.ts_type}"
            if bind.inside_if:
                pre_buffer += " | undefined"
            pre_buffer += ";"

        self.buffer += f"const result: {self.interface_name} = {{rootFragment,"
        for bind in self.binds:
            self.buffer += f"{bind.name}: {bind.uid},"
        self.buffer += "};"
        for helper_run in self.helper_runs:
            self.buffer += helper_run
        self.buffer += "return result;"
        self.buffer += "};"

        self.buffer = pre_buffer + self.buffer

        return ";\n".join(self.buffer.split(";"))

    def handle_starttag(self, tag, attrs):
        self.handle_data(None)

        uid = self.get_next_uid()

        append_to_element_uid = self.current_element_uid

        construct = None
        if tag == "var":
            self.context.add_var(attrs)

        if tag in self.available_templates:
            construct = RainwaveTemplateElement(tag, attrs, uid, append_to_element_uid)
        elif tag in TAG_HANDLERS:
            construct = TAG_HANDLERS[tag](tag, attrs, uid, append_to_element_uid)
        else:
            construct = RainwaveHTMLElement(tag, attrs, uid, append_to_element_uid)

        self.buffer += construct.handle_start()

        self.construct_tree.append(construct)

        if tag == "context":
            self.context = construct

    def handle_endtag(self, end_tag):
        self.handle_data(None)

        try:
            construct = self.construct_tree.pop()
            if end_tag != construct.tag:
                raise Exception(
                    f"{self.name} has mismatched open/close tags. ({self.construct_tree})"
                )
            for template in construct.templates:
                self.add_template(template)
            for bind in construct.binds:
                if any(bind2.name == bind.name for bind2 in self.binds):
                    raise Exception(f"{self.name} added double bind {bind.name}")
                if any(isinstance(ct, RainwaveIfElement) for ct in self.construct_tree):
                    bind.inside_if = True
                self.binds.append(bind)
            for helper in construct.helpers:
                self.add_helper(helper)
                self.helper_runs.append(f"{helper}({construct.uid});")
            self.buffer += construct.handle_end()

        except IndexError:
            raise Exception("%s has too many closing tags." % self.name)

    def handle_data(self, lines):
        if lines:
            self.input_buffer += lines
            return

        self.input_buffer = self.input_buffer.strip()
        if not self.input_buffer:
            return

        if len(self.construct_tree) == 0:
            raise Exception(f"{self.name}: Tried to set textContent of root element.")

        for line in self.input_buffer.split("\n"):
            if "${ $l(" in line:
                self.add_helper("$l")
            self.buffer += f"{self.current_element_uid}.appendChild(document.createTextNode(`{line}`));"
        self.input_buffer = ""

