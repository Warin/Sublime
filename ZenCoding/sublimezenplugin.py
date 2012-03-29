#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import operator
import os

from os.path import join, dirname

# Sublime Libs
import sublime
import sublime_plugin

# Zen Coding libs
from zencoding.parser.abbreviation import ZenInvalidAbbreviation
from zencoding import resources as zcr

# Dynamic Snippet Base Class
from dynamicsnippets import CommandsAsYouTypeBase

import zencoding
import zencoding.actions

from sublimezen import ( expand_abbr, editor, css_sorted,
                         css_property_values, multi_selectable,
                         find_css_property, find_tag_name,
                         find_attribute_name, css_prefixer, find_css_selector)

from zenmeta    import ( CSS_PROP_VALUES, HTML_ELEMENTS_ATTRIBUTES,
                         HTML_ATTRIBUTES_VALUES, CSS_PSEUDO_CLASSES)

from zencoding.html_matcher import last_match

################################### CONSTANTS ##################################

HTML                      = 'text.html - source'
XML                       = 'text.xml'

HTML_INSIDE_TAG_ANYWHERE  = 'text.html meta.tag'
HTML_INSIDE_TAG           = ( 'text.html meta.tag - string - '
                              'meta.scope.between-tag-pair.html '
                              '-punctuation.definition.tag.begin.html')

HTML_INSIDE_TAG_ATTRIBUTE = 'text.html meta.tag string'

HTML_NOT_INSIDE_TAG       = 'text.html - meta.tag'

CSS          = 'source.css, source.scss, source.stylus'
CSS_PROPERTY = 'meta.property-list.css - meta.property-value.css'
CSS_SELECTOR = 'meta.selector.css, source.css - meta, source.scss - meta'

CSS_PROPERTY_NAME =  'meta.property-list.css meta.property-name.css'

CSS_PREFIXER = 'meta.property-list.css, meta.selector.css'
CSS_VALUE    = 'meta.property-list.css meta.property-value.css'

CSS_ENTITY_SELECTOR = 'meta.selector.css entity.other.attribute-name'

ZEN_SCOPE = ', '.join([HTML, XML, CSS])

#################################### AUTHORS ###################################

__version__     = '1.5.0a'

__zen_version__ = '0.7'

__authors__     = ['"Sergey Chikuyonok" <serge.che@gmail.com>'
                   '"Вадим Макеев"      <pepelsbey@gmail.com>',
                   '"Nicholas Dudfield" <ndudfield@gmail.com>']

################################### SETTINGS ###################################

zen_settings = sublime.load_settings('zen-coding.sublime-settings')

OPMAP = {
    sublime.OP_EQUAL     : operator.eq,
    sublime.OP_NOT_EQUAL : operator.ne,
}

def eval_op(op, operand, operand2):
    return OPMAP[op](operand, operand2)

class ZenSettings(sublime_plugin.EventListener):
    def on_query_context(self, view, key, op, operand, match_all):
        if key.startswith('zen_setting'):
            return eval_op(op, operand, zen_settings.get(key.split('.')[1]))

##################################### TODO #####################################
"""

Anything referencing `css_sorted` should be updated to be recalculated on zen-
codings.sublime-settings change)

Installation Docs
    OSX
    Windows
    Linux

"""
#################################### LOGGING ###################################

def debug(f):
    if zen_settings.get('debug'):
        sublime.log_commands(True)
        print 'ZenCoding:', f

def oq_debug(f):
    debug("on_query_completions %s" % f)

################################ MY ZEN SETTINGS ###############################

def load_settings(force_reload=False):
    if not zcr.user_settings or force_reload:
        my_zen_settings = zen_settings.get('my_zen_settings')

        if my_zen_settings is not None:
            debug('loading my_zen_settings from zen-settings.sublime-settings')
            zcr.set_vocabulary(my_zen_settings, zcr.VOC_USER)
            assert zcr.vocabularies[zcr.VOC_USER] is my_zen_settings

load_settings()

if int(sublime.version()) >= 2092:
    zen_settings.clear_on_change('zen_coding')
    zen_settings.add_on_change('zen_coding',
                               lambda: load_settings(force_reload=1))

################################### ARBITRAGE ##################################

try:
    arbited
except NameError:
    arbited = True
    if zen_settings.get('zenarbitrage'):
        from zenarbitrage import doop
        doop()

######################## REMOVE HTML/HTML_COMPLETIONS.PY #######################

def remove_html_completions():
    import sublime_plugin

    for completer in "TagCompletions", "HtmlCompletions":
        try:
            import html_completions
            cm = getattr(html_completions, completer)
        except (ImportError, AttributeError):
            debug('Unable to find `html_completions.HtmlCompletions`')
            continue

        completions = sublime_plugin.all_callbacks['on_query_completions']
        for i, instance in enumerate (completions):
            if isinstance(instance, cm):
                debug('on_query_completion: removing: %s' % cm)
                del completions[i]

        # The funky loader
        if debug: debug('on_query_completion: callbacks: %r' % completions)

sublime.set_timeout(remove_html_completions, 2000)

########################## DYNAMIC ZEN CODING SNIPPETS #########################


class ZenAsYouType(CommandsAsYouTypeBase):
    default_input = 'div'
    input_message = "Enter Koan: "

    def filter_input(self, abbr):
        try:
            return expand_abbr(abbr, super_profile='no_check_valid')
        except Exception:
            "dont litter the console"

class WrapZenAsYouType(CommandsAsYouTypeBase):
    default_input = 'div'
    input_message = "Enter Haiku: "

    def run_command(self, view, cmd_input):
        try:
            ex = expand_abbr(cmd_input, super_profile='no_check_valid')
            p  = editor.get_profile_name() + '.no_check_valid'
            if not ex.strip():
                raise ZenInvalidAbbreviation('Empty expansion %r' % ex)
        except Exception:
            return False

        view.run_command (
            'run_zen_action',
            dict(action="wrap_with_abbreviation",
            abbr=cmd_input, profile_name=p))

################################ RUN ZEN ACTION ################################

class RunZenAction(sublime_plugin.TextCommand):
    last_matches = []

    @multi_selectable
    def run(self, view, contexter, kw):
        matches = []

        for i, selection in enumerate(contexter):
            args = kw.copy()

            if self.last_matches and not i >= len(self.last_matches):
                last_match.update(self.last_matches[i])

            zencoding.run_action(args.pop('action'), editor, **args)
            matches.append(last_match.copy())

        self.last_matches = matches

################################# ZEN MNEMONIC #################################

class ZenCssMnemonic(sublime_plugin.WindowCommand):
    " Insert css snippets from QuickPanel"

    def is_enabled(self, **args):
        return len(self.window.active_view().sel()) == 1

    def run(self, prop_value=False):
        window = self.window
        view = window.active_view()

        if prop_value:
            pos      = view.sel()[0].b
            prop     = find_css_property(window.active_view(), pos)
            forpanel = sorted((css_property_values.get(prop) or {}).items())
            contents = lambda i: forpanel[i][1]
            # TODO expand while selector matches
            "meta.property-value.css - punctuation"
            # Then insert snippet over top of selection
        else:
            forpanel = css_sorted
            contents = lambda i: expand_abbr(forpanel[i][0])

        def done(i):
            if i != -1:
                view.run_command('insert_snippet', {'contents': contents(i)})

        display  = [[v,k] for k,v in forpanel]
        window.show_quick_panel(display, done)

################################### CONTEXTS ###################################

class ZenListener(sublime_plugin.EventListener):
    def correct_syntax(self, view):
        return view.match_selector( view.sel()[0].b, ZEN_SCOPE )

    def css_selectors(self, view, prefix, pos):
        elements = [ (v, v) for v in
                     sorted(HTML_ELEMENTS_ATTRIBUTES.keys()) if v != prefix]

        if view.syntax_name(pos).strip() in ('source.scss', 'source.css'):
            return elements
        else:
            selector = find_css_selector(view, pos)
            oq_debug('css_selectors selector: %r' % selector)

            if ':' in selector:
                prefix = selector.rsplit(':', 1)[-1]
                return [ ( prefix, (':' + p), p.replace('|', '$1') ) for p in
                           CSS_PSEUDO_CLASSES if
                           not prefix or p.startswith(prefix[0].lower() ) ]
            elif selector.startswith('.'):
                return []
                # return []
                return [(selector, v, v) for v in
                     set(map(view.substr, [
                         r for r in view.find_by_selector('source.css '
                       'meta.selector.css entity.other.attribute-name.class.css')
                          if not r.contains(pos)] ))]
            else:
                return elements

    def css_property_values(self, view, prefix, pos):
        prefix = css_prefixer(view, pos)
        prop   = find_css_property(view, pos)
        # These `values` are sourced from all the fully specified zen abbrevs
        # `d:n` => `display:none` so `display:n{tab}` will yield `none`
        values = css_property_values.get(prop)

        if values and prefix and prefix in values:
            oq_debug("zcprop:val prop: %r values: %r" % (prop, values))
            return [(d, '%s\t(%s)' % (v, d), v) for d,v in sorted(values.items())]
        else:
            # Look for values relating to that property
            # Remove exact matches, so a \t is inserted
            values =  [v for v in CSS_PROP_VALUES.get(prop, []) if v != prefix]
            if values:
                debug("zenmeta:val prop: %r values: %r" % (prop, values))
                return [(v,  v, v) for v in values]
                # return [(v,  '%s\t(%s)' % (v, v), v) for v in values]

    def html_elements_attributes(self, view, prefix, pos):
        tag         = find_tag_name(view, pos)
        values      = HTML_ELEMENTS_ATTRIBUTES.get(tag, [])
        return [(v,   '%s\t@%s' % (v,v), '%s="$1"' % v) for v in values]

    def html_attributes_values(self, view, prefix, pos):
        attr        = find_attribute_name(view, pos)
        values      = HTML_ATTRIBUTES_VALUES.get(attr, [])
        return [(v, '%s\t@=%s' % (v,v), v) for v in values]

    def on_query_completions(self, view, prefix, locations):
        if ( not self.correct_syntax(view) or
             zen_settings.get('disable_completions', False) ): return []

        black_list = zen_settings.get('completions_blacklist', [])

        # We need to use one function rather than discrete listeners so as to
        # avoid pollution with less specific completions. Try to return early
        # with the most specific match possible.

        oq_debug("prefix: %r" % prefix)

        # A mapping of scopes, sub scopes and handlers, first matching of which
        # is used.
        COMPLETIONS = (
            (CSS_SELECTOR,              self.css_selectors),
            (CSS_VALUE,                 self.css_property_values),
            (HTML_INSIDE_TAG,           self.html_elements_attributes),
            (HTML_INSIDE_TAG_ATTRIBUTE, self.html_attributes_values) )

        pos = view.sel()[0].b

        # Try to find some more specific contextual abbreviation
        for sub_selector, handler in COMPLETIONS:
            h_name = handler.__name__
            if h_name in black_list: continue
            if view.match_selector(pos,  sub_selector):

                c = h_name, prefix
                oq_debug('handler: %r prefix: %r' % c)
                oq_debug('pos: %r scope: %r' % (pos, view.syntax_name(pos)))

                completions = handler(view, prefix, pos)
                oq_debug('completions: %r' % completions)
                if completions: return completions

        do_zen_expansion = True
        html_scope_for_zen = ("text.html meta.tag "
                "-meta.scope.between-tag-pair.html "
                "-punctuation.definition.tag.begin.html")

        if view.match_selector(pos, 'text.html'):
            if view.match_selector(pos, html_scope_for_zen):
                do_zen_expansion = False

        if do_zen_expansion:
            # Expand Zen expressions such as `d:n+m:a` or `div*5`
            try:

                abbr = zencoding.actions.basic.find_abbreviation(editor)
                oq_debug('abbr: %r' % abbr)
                if abbr and not view.match_selector( locations[0],
                                                     HTML_INSIDE_TAG ):
                    result = expand_abbr(abbr)
                    oq_debug('expand_abbr abbr: %r result: %r' % (abbr, result))

                    if result:
                        return [(abbr, result, result)]

            except ZenInvalidAbbreviation:
                pass

        # If it wasn't a valid Zen css snippet, or the prefix is empty ''
        # then get warm and fuzzy with css properties.

        # TODO, before or after this, fuzz directly against the zen snippets
        # eg  `tjd` matching `tj:d` to expand `text-justify:distribute;`

        if ( view.match_selector(pos, CSS_PROPERTY) and
             not 'css_properties' in black_list ):

            # Use this to get non \w based prefixes
            prefix     = css_prefixer(view, pos)
            properties = sorted(CSS_PROP_VALUES.keys())
            # 'a'.startswith('') is True! so will never get IndexError below
            exacts     = [p for p in properties if p.startswith(prefix)]

            if exacts: properties = exacts
            else:      properties = [ p for p in properties if
                                      # to allow for fuzzy, which will
                                      # generally start with first letter
                                      p.strip('-').startswith(prefix[0].lower()) ]

            oq_debug('css_property exact: %r prefix: %r properties: %r' % (
                      bool(exacts), prefix, properties ))

            return [ (prefix, v, '%s:$1;' %  v) for v in properties ]
        else:
            return []

    @staticmethod
    def check_context(view):
        abbr        =       zencoding.actions.basic.find_abbreviation(editor)
        if abbr:
            try:            result = expand_abbr(abbr)
            except          ZenInvalidAbbreviation: return None
            if result:
                return result

    def on_query_context(self, view, key, op, operand, match_all):
        if key == 'is_zen':
            debug('checking iz_zen context')
            context = ZenListener.check_context(view)

            if context is not None:
                debug('is_zen context enabled')
                return True
            else:
                debug('is_zen context disabled')
                return False

################################################################################

class SetHtmlSyntaxAndInsertSkel(sublime_plugin.TextCommand):
    def run(self, edit, doctype=None):
        view     = self.view
        syntax   = zen_settings.get( 'default_html_syntax',
                                     'Packages/HTML/HTML.tmlanguage' )
        view.set_syntax_file(syntax)
        view.run_command( 'insert_snippet',
                          {'contents': expand_abbr('html:%s' % doctype)} )

################################################################################