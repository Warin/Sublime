#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Standard Libs
import re

# Sublime Libs
import sublime
import sublime_plugin

################################## BASE CLASS ##################################

class CommandsAsYouTypeBase(sublime_plugin.TextCommand):
    history = {}
    filter_input = lambda s, i: i

    def run_command(self, view, value):
        if '\n' in value:
            for sel in view.sel():
                trailing = sublime.Region(sel.end(), view.line(sel).end())
                if view.substr(trailing).isspace():
                    view.erase(self.edit, trailing)

        view.run_command('insert_snippet', { 'contents': value })

    def insert(self, abbr):
        view = self.view

        if not abbr and self.erase:
            self.undo()
            self.erase = False
            return

        def inner_insert():
            self.edit = edit = view.begin_edit()
            cmd_input  = self.filter_input(abbr) or ''
            self.erase = self.run_command(view, cmd_input) is not False
            view.end_edit(edit)

        self.undo()
        sublime.set_timeout(inner_insert, 0)

    def undo(self):
        if self.erase:
            sublime.set_timeout(lambda: self.view.run_command('undo'), 0)

    def run(self, edit, **args):
        self.erase = False

        panel = self.view.window().show_input_panel (
          self.input_message, self.default_input, None, self.insert, self.undo )
        
        panel.sel().clear()
        panel.sel().add(sublime.Region(0, panel.size()))

################################################################################