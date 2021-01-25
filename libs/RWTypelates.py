import os
import re
import typing
from html.parser import HTMLParser

# TODO: binds in ifs need ? in interface


def compile_templates():
    source_dir = "."
    templates = {}
    for root, _subdirs, files in os.walk(source_dir):
        for filename in files:
            if filename.endswith(".hbar"):
                include_location = os.path.join(
                    root[len(source_dir) + 1 :], filename[: filename.rfind(".")],
                )
                template_name = filename[:-5]
                templates[template_name] = include_location

    helpers = {}
    for root, _subdirs, files in os.walk(os.path.join(source_dir, "templateHelpers")):
        for filename in files:
            if filename.endswith(".ts"):
                helpers[filename[0:-3]] = os.path.join(
                    root[len(source_dir) + 1 :], filename[0:-3]
                )

    helpers["$l"] = helpers["gettext"]

    for template_name, include_location in templates.items():
        with open(include_location + ".hbar") as template_file:
            with open(include_location + ".template.ts", "w") as out_file:
                parser = RainwaveParser(
                    template_name, templates=templates, helpers=helpers,
                )
                parser.feed(template_file.read())
                out_file.write(parser.close())


def parse_attr_value(value: str) -> str:
    if isinstance(value, str):
        lookup_value = value.strip('"')
        if lookup_value[0] == "$":
            return f"context.{lookup_value[1:]}"
        return value
    return value


def get_template_type_name(template: str) -> str:
    return template[0].upper() + template[1:] + "Template"


class RainwaveElement:
    tag: str
    uid: str
    append_to_element_uid: str
    attrs: list
    binds: dict
    helpers: list
    templates: list
    types: list

    def __init__(self, tag: str, attrs: list, uid: str, append_to_element_uid: str):
        self.tag = tag
        self.attrs = attrs
        self.uid = uid
        self.append_to_element_uid = append_to_element_uid

        self.binds = {}
        self.helpers = []
        self.templates = []
        self.types = []

    def __str__(self):
        return f"<{self.__class__.__name__} {self.tag} {self.attrs} {self.uid}>"

    def __repr__(self):
        return str(self)

    def handle_start(self) -> str:
        raise NotImplementedError

    def handle_end(self) -> str:
        raise NotImplementedError

    def parse_attr_value(self, value: str) -> str:
        return parse_attr_value(value)

    @property
    def element_uid(self):
        return self.append_to_element_uid


class RainwaveHTMLElement(RainwaveElement):
    def handle_start(self) -> str:
        uid = self.uid
        tag = self.tag
        attrs = self.attrs

        buffer = f"const {uid}=document.createElement('{tag}');"
        for [attr, raw_value] in attrs:
            value = self.parse_attr_value(raw_value)
            if attr == "bind":
                typescript_type = tag[0].upper() + tag[1:]
                self.binds[value] = f"HTML{typescript_type}Element"
            elif attr == "class":
                classes = []
                for class_name in raw_value.split(" "):
                    if class_name.startswith("$className__"):
                        rest = class_name.split("__", limit=1)[1]
                        classes.append(f"${{context.className}}__{rest}`")
                    else:
                        classes.append(value)
                class_attrib = " ".join(classes)
                buffer += f"{uid}.className=`{class_attrib}`;"
            elif attr == "href":
                buffer += f"{uid}.href='{value}';"
            elif attr == "helper":
                self.helpers.append(value)
            else:
                html_value = value or r"''"
                buffer += f"{uid}.setAttribute('{attr}',{html_value});"
        buffer += f"{self.append_to_element_uid}.appendChild({uid});"
        return buffer

    def handle_end(self) -> str:
        return ""

    @property
    def element_uid(self):
        return self.uid


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
        left_value = parse_attr_value(left[1])
        result += f"{left_value}"
        if op and right:
            right_value = parse_attr_value(right[1])
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

    def handle_end(self):
        return "}"


class RainwaveElsifElement(RainwaveIfElement):
    def handle_start(self) -> str:
        if_start = super().handle_start()
        return f"else {if_start}"


class RainwaveElseElement(RainwaveElement):
    def handle_start(self) -> str:
        return "else {"

    def handle_end(self) -> str:
        return "}"


class RainwaveForeachElement(RainwaveElement):
    def handle_start(self) -> str:
        attrs = self.attrs
        array_name = self.parse_attr_value(
            next((attr for attr in attrs if attr[0] == "array"), None)
        )
        return f"{array_name}.forEach(context => {{"

    def handle_end(self) -> str:
        return "});"


class RainwaveTemplateElement(RainwaveElement):
    def handle_start(self) -> str:
        self.templates.append(self.tag)
        subtemplate_context_type = "null"
        subtemplate_context = next(
            (attr[1] for attr in self.attrs if attr[0] == "context"), None
        )
        if not subtemplate_context:
            raise Exception(f"{self} subtemplate has no context.")
        elif subtemplate_context == "this":
            subtemplate_context_type = "Context"
            subtemplate_context = "context"
        else:
            subtemplate_context_type = f"Context['{subtemplate_context}']"
            subtemplate_context = f"context.{subtemplate_context}"
        bind_name = next(
            (attr[1] for attr in self.attrs if attr[0] == "bind"), self.tag
        )
        self.binds[bind_name] = get_template_type_name(self.tag)
        return f"const {self.uid}={self.tag}<{subtemplate_context_type}>({subtemplate_context}, {self.append_to_element_uid});"

    def handle_end(self) -> str:
        return ""


class RainwaveContextElement(RainwaveElement):
    buffer: str

    def handle_start(self) -> str:
        self.buffer = "interface Context {"
        for (iname, itype) in self.attrs:
            itype_to_write = itype
            if itype.startswith("$"):
                itype = itype[1:]
                itype_to_write = itype[0].upper() + itype[1:] + "Type"
                self.types.append((itype_to_write, itype))
            self.buffer += f"{iname}: {itype_to_write}"
        self.buffer += "}\n\n"
        return ""

    def handle_end(self) -> str:
        return ""


TAG_HANDLERS = {
    "if": RainwaveIfElement,
    "else": RainwaveElseElement,
    "elsif": RainwaveElsifElement,
    "context": RainwaveContextElement,
}


class RainwaveParser(HTMLParser):
    UNIQUE_ID_CHARS = [chr(x) for x in range(65, 91)] + [chr(x) for x in range(97, 123)]
    name: str
    construct_tree: typing.List[RainwaveElement]
    input_buffer: str
    buffer: str
    interface_name: str
    interface: typing.Dict[str, str]
    includes: typing.Dict[str, str]
    binds: typing.Dict[str, str]
    helper_runs: typing.List[str]
    helpers: typing.Dict[str, str]
    templates: typing.Dict[str, str]
    context: RainwaveContextElement

    _current_unique_id: str

    def __init__(self, template_name: str, templates: dict, helpers: dict):
        super().__init__()

        self.name = template_name
        self.construct_tree = []
        self.input_buffer = ""
        self.buffer = ""
        self.interface = {
            "rootFragment": "DocumentFragment",
        }
        self.includes = {}
        self.binds = {}
        self.helper_runs = []
        self.helpers = helpers
        self.templates = templates

        self._current_unique_id = self.UNIQUE_ID_CHARS[0]

        self.interface_name = template_name[0].upper() + template_name[1:] + "Template"

        self.buffer += f"export default function {template_name} ("
        self.buffer += r"  context: Context, "
        self.buffer += (
            r"  rootFragment: DocumentFragment = document.createDocumentFragment()"
        )
        self.buffer += f"): {self.interface_name} {{"

    def get_next_uid(self):
        next_idx = self.UNIQUE_ID_CHARS.index(self._current_unique_id[-1]) + 1
        if next_idx >= len(self.UNIQUE_ID_CHARS):
            self._current_unique_id += self.UNIQUE_ID_CHARS[0]
        else:
            self._current_unique_id = (
                self._current_unique_id[:-1] + self.UNIQUE_ID_CHARS[next_idx]
            )
        return self._current_unique_id

    def add_helper(self, helper):
        if not helper in self.helpers:
            raise Exception(f"{self.name} called nonexistent helper {helper}")
        self.includes[helper] = self.helpers[helper]

    def add_template(self, template):
        if not template in self.templates:
            raise Exception(f"{self.name} called nonexistent template {template}")
        self.includes[get_template_type_name(template)] = (
            self.templates[template] + ".template"
        )

    @property
    def current_uid(self):
        if len(self.construct_tree) == 0:
            return "rootFragment"
        else:
            return self.construct_tree[-1].uid

    def close(self, *args, **kwargs):
        self.handle_data(None)

        super().close(*args, **kwargs)

        if len(self.construct_tree) > 0:
            stack = "\n".join(self.construct_tree)
            raise Exception(f"{self.name} unclosed stack: {stack}")

        pre_buffer = ""

        for include, include_location in self.includes.items():
            pre_buffer += f"import * as {include} from '{include_location}';"

        for (itype_name, itype) in self.context.types:
            pre_buffer += f"import * as {itype_name} from 'types/{itype}';"

        pre_buffer += f"\n\ninterface {self.interface_name} {{"
        for key, var_type in self.interface.items():
            pre_buffer += f"{key}: {var_type};"
        pre_buffer += "}\n\n"

        pre_buffer += self.context.buffer

        self.buffer += f"const result: {self.interface_name} = {{rootFragment,"
        for bind_name, bind_value in self.binds.items():
            self.buffer += f"{bind_name}: {bind_value},"
        self.buffer += "};"
        for helper_run in self.helper_runs:
            self.buffer += helper_run
        self.buffer += "return result;"
        self.buffer += "};"

        self.buffer = pre_buffer + self.buffer

        return ";\n".join(self.buffer.split(";"))

    def get_append_to_element_uid(self) -> str:
        append_to_element_uid = "rootFragment"
        if len(self.construct_tree) > 0:
            append_to_element_uid = self.construct_tree[-1].element_uid
        return append_to_element_uid

    def handle_starttag(self, tag, attrs):
        self.handle_data(None)

        uid = self.get_next_uid()

        append_to_element_uid = self.get_append_to_element_uid()

        construct = None
        if tag in self.templates:
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
            for bind_name, bind_type in construct.binds.items():
                if bind_name in self.interface:
                    raise Exception(f"{self.name} added double bind {bind_name}")
                self.interface[bind_name] = bind_type
                self.binds[bind_name] = construct.uid
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

        append_to_element_uid = self.get_append_to_element_uid()

        for line in self.input_buffer.split("\n"):
            for text_segment in re.split(r"({{.*?}})", line):
                text_segment = text_segment.strip()
                if not text_segment or len(text_segment) == 0:
                    pass
                text = ""
                if text_segment[:2] == "{{" and text_segment[-2:] == "}}":
                    stripped = text_segment[2:-2].strip()
                    if stripped[:3] == "$l(":
                        self.add_helper("$l")
                        text = f"$l({stripped[3:-1]})"
                    else:
                        text = parse_attr_value(stripped)
                elif r'"' in text_segment:
                    raise Exception(
                        f"{self.name}: Double-quotes in text content are not allowed."
                    )

                if text.strip('"'):
                    self.buffer += f"{append_to_element_uid}.appendChild(document.createTextNode({text}));"
        self.input_buffer = ""


if __name__ == "__main__":
    compile_templates()

