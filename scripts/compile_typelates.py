#!/usr/bin/env python

import os

from typelates.parser import RainwaveParser

if __name__ == "__main__":
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
