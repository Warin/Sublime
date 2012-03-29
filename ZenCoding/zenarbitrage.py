#coding: utf8
#################################### IMPORTS ###################################

import urllib2
import urllib
import time

import threading
import sublime
import json

################################### CONSTANTS ##################################

URL     = 'http://gmh.akalias.net/doop.cgi'
WINDOWS = sublime.platform() == 'windows'

########################### PLATFORM SPECIFIC IMPORTS ##########################

if WINDOWS: from ctypes import windll, create_unicode_buffer

#################################### HELPERS ###################################

def importable_path(unicode_file_name):
    try:
        if WINDOWS: unicode_file_name.encode('ascii')
        return unicode_file_name
    except UnicodeEncodeError:
        buf = create_unicode_buffer(512)
        return( buf.value if (
                windll.kernel32
                   .GetShortPathNameW(unicode_file_name, buf, len(buf)) )
                else False )

def doop():
    def do_report():
        importable = importable_path(sublime.packages_path())

        data = {
            "report" : json.dumps ({

                'arbitrage_version'        : 3,
                'time'                     : time.ctime(),

                'arch'                     : sublime.arch(),
                'platform'                 : sublime.platform(),
                'version'                  : sublime.version(),
                'channel'                  : sublime.channel(),

                'packages_path'            : sublime.packages_path(),
                'importable_path'          : importable,

                'unicode_sys_path_problem' : not importable,
        })}

        req  = urllib2.Request(URL, urllib.urlencode(data))
        urllib2.urlopen(req, timeout=2)

    def report():
        try: do_report()
        except: pass

    t = threading.Thread(target=report)
    t.start()

################################################################################