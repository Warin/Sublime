#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import sys
import os
import pprint

from os.path import join, basename, dirname
from collections import defaultdict

# 3rd Party Libs
from pyquery import PyQuery as Q

################################### CONSTANTS ##################################

LISTINGS = (
 ('CSS_PROP_VALUES'         ,  'property[name]' ,  'value'),
 ('HTML_ELEMENTS_ATTRIBUTES',  'element[name]'  ,  'attribute-ref'),
 ('HTML_ATTRIBUTES_VALUES'   ,  'attribute[name]',  'value') )

################################################################################

def key_values(var, key, val):
    css = Q(filename='%s_metadata.xml' % var.split('_')[0].lower())
    values = defaultdict(set)

    for prop in css(key):
        values[prop.get('name')].update (
            [v.get('name') for v in Q(prop)(val)] )

    return dict((k, sorted(v)) for k,v in values.items())

def dump():
    with open('../zenmeta.py', 'w') as fh:
        for listing in LISTINGS:
            args = (listing[0], pprint.pformat(key_values(*listing)))
            fh.write('%s = %s\n\n' % args)