import sublime_plugin
import sublime
import re


#   : element_name [ HASH | class | attrib | pseudo ]*
#   | [ HASH | class | attrib | pseudo ]+
class CsspecificCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view

        ident = "[a-zA-Z_](?:[a-zA-Z0-9_\\-]*)"  # an identifier
        reTag = re.compile(ident)
        reId = re.compile("#" + ident)
        reClass = re.compile("\\." + ident)
        reType = re.compile("\\[\\s*\\S.*?\\]")
        rePseudo = re.compile(":" + ident + "(?:\\(.*?\\))?")
        rePseudoTag = re.compile(":(?:link|visited|active|hover|focus|first-letter|first-line|first-child|before|after|lang)")
        reStar = re.compile("\\*")

        for sel in v.sel():
            if not sel.empty():
                intersect = True
                break
        else:
            intersect = False

        output = []
        for rules in v.find_by_selector('meta.selector.css'):
            skip = False
            if intersect:
                skip = True
                for sel in v.sel():
                    if rules.intersects(sel):
                        skip = False
                        break

            if skip:
                continue

            for rule in re.split("\\s*,\\s*", v.substr(rules)):
                score = 0
                for selector in re.split("\\s*[+> ]+\\s*", rule):
                    while len(selector):
                        while True:
                            match = reTag.match(selector)
                            if match:
                                score += 1
                                break

                            match = reId.match(selector)
                            if match:
                                score += 100
                                break

                            match = reClass.match(selector)
                            if match:
                                score += 10
                                break

                            match = reType.match(selector)
                            if match:
                                score += 10
                                break

                            match = rePseudo.match(selector)
                            if match:
                                if (rePseudoTag.match(selector)):
                                    score += 1
                                else:
                                    score += 10
                                break

                            match = reStar.match(selector)
                            break
                        if match:
                            token = match.group(0)
                            selector = selector[len(token):]
                        else:
                            output.append("Couldn't match %s" % selector)
                            break
                output.append("/* %03d */ %s" % (score, rule))
        self.panel("\n".join(output))

    def panel(self, output, **kwargs):
        if not hasattr(self, 'output_view'):
            self.output_view = self.get_window().get_output_panel("csspecific")
        self.output_view.set_read_only(False)
        self._output_to_view(self.output_view, output, clear=True, **kwargs)
        self.output_view.set_read_only(True)
        self.get_window().run_command("show_panel", {"panel": "output.csspecific"})

    def _output_to_view(self, output_file, output, clear=False):
        output_file.set_syntax_file("Packages/CSS/CSS.tmLanguage")
        edit = output_file.begin_edit()
        if clear:
            region = sublime.Region(0, self.output_view.size())
            output_file.erase(edit, region)
        output_file.insert(edit, 0, output)
        output_file.end_edit(edit)

    def get_window(self):
        return self.view.window()
