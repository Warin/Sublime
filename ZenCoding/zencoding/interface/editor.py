#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import unittest
import functools
import sys
import os
import re
import pprint

from zencoding import utils, expand_abbreviation

# Sublime modules
try:
    import sublime
except ImportError:
    sublime = None

#################################### HELPERS ###################################

def active_view():
    return sublime.active_window().active_view()

################################################################################

class ZenEditor():
    def expand_abbr(self, abbr, syntax = None, selection=True,
                                               super_profile=None):

        syntax       = syntax or self.get_syntax()
        profile_name = self.get_profile_name()

        if super_profile: profile_name += '.%s' % super_profile
        content      = expand_abbreviation(abbr, syntax, profile_name)

        return ( self.add_placeholders(content, selection=selection) )

    def __init__(self):
        pass

    def set_context(self, context):
        """
        Setup underlying editor context. You should call this method
        *before* using any Zen Coding action.
        @param context: context object
        """
        print 'setting context', repr(context)


    def get_selection_range(self):
        """
        Returns character indexes of selected text
        @return: list of start and end indexes
        @example
        start, end = zen_editor.get_selection_range();
        print('%s, %s' % (start, end))
        """
        view = active_view()
        sel = view.sel()[0]
        return sel.begin(), sel.end()

    def create_selection(self, start=None, end=None, sels=[]):
        """
        Creates selection from *start* to *end* character
        indexes. If *end* is ommited, this method should place caret
        and *start* index
        @type start: int
        @type end: int
        @example
        zen_editor.create_selection(10, 40)
        # move caret to 15th character
        zen_editor.create_selection(15)
        """


        view = active_view()
        view.sel().clear()

        for start, end in (sels or [(start, end)]):
            view.sel().add(sublime.Region(start, end or start))

        view.show(view.sel())

    def get_current_line_range(self):
        """
        Returns current line's start and end indexes
        @return: list of start and end indexes
        @example
        start, end = zen_editor.get_current_line_range();
        print('%s, %s' % (start, end))
        """
        view = active_view()
        selection = view.sel()[0]
        line = view.line(selection)
        return line.begin(), line.end()

    def get_file_path(self):
        return active_view().file_name()

    def get_caret_pos(self):
        """ Returns current caret position """
        view = active_view()
        return len(view.sel()) and view.sel()[0].begin() or 0

    def set_caret_pos(self, pos):
        """
        Set new caret position
        @type pos: int
        """
        self.create_selection(pos)

    def get_current_line(self):
        """
        Returns content of current line
        @return: str
        """
        view = active_view()
        return view.substr(view.line(view.sel()[0]))

    def replace_content(self, value, start=None, end=None, zero_stops=False, 
                              escape = True):
        """
        Replace editor's content or it's part (from *start* to
        *end* index). If *value* contains
        *caret_placeholder*, the editor will put caret into
        this position. If you skip *start* and *end*
        arguments, the whole target's content will be replaced with
        *value*.

        If you pass *start* argument only,
        the *value* will be placed at *start* string
        index of current content.

        If you pass *start* and *end* arguments,
        the corresponding substring of current target's content will be
        replaced with *value*
        @param value: Content you want to paste
        @type value: str
        @param start: Start index of editor's content
        @type start: int
        @param end: End index of editor's content
        @type end: int
        """
        view = active_view()
        edit = view.begin_edit()

        if start is None: start = 0
        if end is None:   end   = start

        self.create_selection(start, end)

        # print value
        if escape:
            value = value.replace('$', r'\$')

        value = self.add_placeholders(value,
            selection     = 0, 
            explicit_zero = zero_stops
        )

        if '\n' in value:
            for sel in view.sel():
                trailing = sublime.Region(sel.end(), view.line(sel).end())
                if view.substr(trailing).isspace():
                    view.erase(edit, trailing)

        view.run_command('insert_snippet', {'contents': value})
        view.end_edit(edit)

    def get_content(self):
        """
        Returns editor's content
        @return: str
        """
        view = active_view()
        return view.substr(sublime.Region(0, view.size()))

    def get_syntax(self):
        """
        Returns current editor's syntax mode
        @return: str
        """
        view = active_view()
        scope = view.syntax_name(view.sel()[0].begin())
        default_type = 'html'
        doc_type = None

        try:
            if 'xsl' in scope:
                doc_type = 'xsl'
            else:
                doc_type = re.findall(r'\bhtml|js|css|xml|haml|stylus\b', scope)[0]
                # if doc_type == 'stylus': doc_type = 'css'
                # Sublime has back to front scopes ....
        except:
            doc_type = default_type

        if not doc_type: doc_type = default_type
        return doc_type

    def get_profile_name(self):
        """
        Returns current output profile name (@see zen_coding#setup_profile)
        @return {String}
        """

        KEY     = 'zencoding.profile'
        view    = active_view()

        profile = view.settings().get(KEY, None)
        if profile is not None: return profile

        pos     = self.get_caret_pos()

        if view.match_selector(pos, 'text.xml'):
            return 'xml'

        if view.match_selector(pos, 'text.html'):
            if 'xhtml' in view.substr(sublime.Region(0, 1000)).lower():
                return 'xhtml'
            else:
                return 'html'
        else:
            return 'plain'

    def prompt(self, title):
        """
        Ask user to enter something
        @param title: Dialog title
        @type title: str
        @return: Entered data
        @since: 0.65
        """
        raise NotImplementedError('Ask Skinner')
        return ''

    def get_selection(self):
        """
        Returns current selection
        @return: str
        @since: 0.65
        """
        view = active_view()
        return view.substr(view.sel()[0]) if view.sel() else ''

    def add_placeholders(self, text, selection=True, explicit_zero=False):
        _ix = [-1 if explicit_zero else 1000]

        def get_ix(m):
            _ix[0] += 1
            return '$%s' % _ix[0]

        # text = re.sub(r'\$', '\\$', text)
        text = re.sub(utils.get_caret_placeholder(), get_ix, text)

        if selection:
            # The last placeholder will contain the selected text, if any
            text = re.sub('\$(%s)' % _ix[0], r'${\1:$SELECTION}', text)

        return text