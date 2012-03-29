#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import sys
import os
import pprint
import re

import sublime

from os.path import join
from itertools import chain
from collections import defaultdict
from functools import wraps

################################## ZEN IMPORTS #################################

# Some may not be needed, and maybe not any at all, but in version 0.6 of Zen
# there were some runtime imports, so get these all in sys.modules now before
# the current directory '.' changes. Saves having to put an absolute path in
# `sys.path`

import zencoding
import zencoding.actions
import zencoding.actions.basic
import zencoding.actions.token
import zencoding.actions.traverse
import zencoding.filters
import zencoding.html_matcher
import zencoding.interface
import zencoding.interface.editor
import zencoding.interface.file
import zencoding.parser
import zencoding.parser.abbreviation
import zencoding.parser.css
import zencoding.parser.utils
import zencoding.parser.xml
import zencoding.resources
import zencoding.utils
import zencoding.zen_settings

from zencoding.interface.editor import ZenEditor
from zentrackers import back_track, track_regex, track_scope

################################### CONSTANTS ##################################

CSS_PROP     = 'meta.property-list.css meta.property-name.css'
CSS_SELECTOR = 'meta.selector.css'
ENCODING     = 'utf8' # TODO

##################################### INIT #####################################

editor = ZenEditor()
expand_abbr = editor.expand_abbr

def decode(s):
    return s.decode(ENCODING, 'ignore')

###################################### CSS #####################################

css_snippets = {}

zr = zencoding.resources
for vocab in zr.VOC_SYSTEM, zr.VOC_USER:
    for link in zr.create_resource_chain(vocab, 'css', 'snippets'):
        css_snippets.update(link)

del vocab, link
css_sorted = sorted(tuple(map(decode, i)) for i in css_snippets.items())

@apply
def css_property_values():
    expanded = {}
    property_values = defaultdict(dict)

    for k in [k for k in css_snippets if ':' in k]:
        prop, value =  k.split(':') # abbreviation

        if prop not in expanded:
            prop = expanded[prop] = css_snippets[prop].split(':')[0]
        else:
            prop = expanded[prop]

        property_values[prop][value] = ( 
            css_snippets[k].split(':')[1].rstrip(';'))

    return property_values

############################### MULTI SELECTIONS ###############################

def selections_context(view, ctxt_key = '__ctxter__'):
    sels = list(view.sel())

    def merge():
        view.sel().clear()
        for sel in view.get_regions(ctxt_key):
            view.sel().add(sel)

        view.erase_regions(ctxt_key)
    
    def contexter():
        for sel in reversed(sels):
            view.sel().clear()
            view.sel().add(sel)

            yield sel # and run user code
            view.add_regions ( ctxt_key,
                (view.get_regions(ctxt_key) + list(view.sel())) , '')
    
    return contexter(), merge

def multi_selectable(f):
    @wraps(f)
    def wrapper(self, edit, **args):
        contexter, merge = selections_context(self.view)
        f(self, self.view, contexter, args)
        merge()
    return wrapper

################################### TRACKERS ###################################

def css_prefixer(view, pt):
    region = back_track( view, pt, lambda v, p:
                                   not view.substr(p).isspace() and
                                   not view.match_selector(p, 'punctuation'))[0]

    return view.substr(region if region is not None else sublime.Region(pt, pt))

def find_css_property(view, start_pt):
    conds   = track_scope(CSS_PROP, False), track_scope(CSS_PROP)
    regions = back_track(view, start_pt, *conds)
    return view.substr(regions[-1])

def find_css_selector(view, start_pt):
    conds = [track_scope(CSS_SELECTOR)]
    
    if not sublime.score_selector(view.scope_name(start_pt), CSS_SELECTOR):
    # if not view.score_selector((start_pt), CSS_SELECTOR):
        conds.insert(0, track_scope(CSS_SELECTOR, False))
    
    selector = back_track(view, start_pt, *conds)[-1]

    if selector is not None:
        return view.substr(selector).strip()

def find_tag_start(view, start_pt):
    regions = back_track(view, start_pt, track_regex('<', False) )
    return regions[-1].begin()

def find_tag_name(view, start_pt):
    tag_region = view.find('[a-zA-Z:]+', find_tag_start(view, start_pt))
    name       = view.substr( tag_region )
    return name

def find_attribute_name(view, start_pt):
    conds   = track_scope('string'), track_regex('\s|='), track_regex('\S')
    regions = back_track(view, start_pt, *conds)
    return view.substr(regions[-1])

################################################################################