#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Process CSS properties: replaces snippets, augumented with ! char, with
<em>!important</em> suffix
@author Sergey Chikuyonok (serge.che@gmail.com)
@link http://chikuyonok.ru
'''
import re
import zencoding

from zencoding.parser.abbreviation import ZenInvalidAbbreviation
re_important = re.compile(r'(.+)\!$')

class ZenInvalidCSSAbbreviation(ZenInvalidAbbreviation): pass

@zencoding.filter('css')
def process(tree, profile):
    for item in tree.children:
        # CSS properties are always snippets
        if item.type == 'snippet':
            if re_important.search(item.real_name):
                item.start = re.sub(r'(;?)$', ' !important\\1', item.start)
        else:
            raise ZenInvalidCSSAbbreviation (
                '%r is not a valid CSS Abbreviation' % item.real_name )

        process(item, profile)
    return tree