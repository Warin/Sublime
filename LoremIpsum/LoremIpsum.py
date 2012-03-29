import sublime, sublime_plugin
import random

class LoremIpsumCommand(sublime_plugin.TextCommand):
    def run(self, edit, qty = 10):
        selections = self.view.sel()
        for selection in selections:
            # always start with Lorem ipsum
            para = "Lorem ipsum ";
            # words from the original Lorum ipsum text
            words = "dolor sit amet consectetur adipisicing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".split()

            from random import choice
            for x in range(random.randint(qty - qty/2, qty + qty/2)):
                para += choice(words) + " "
            para += choice(words) + ". "
            editor = self.view.begin_edit()

            # erase region
            self.view.erase(editor, selection)
            # insert para before current cursor position
            self.view.insert(editor, selection.begin(), para)

            # insert para over the top of selection, but remaining selected (not behavior we want)
            # self.view.replace(editor, self.view.sel()[0], para)

            self.view.end_edit(editor)