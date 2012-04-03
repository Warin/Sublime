import sys, os, sublime, sublime_plugin
from modules import cssvariables, cssnesting
import tests

#
# Text Commands
#

class css_less_ish_compile_command(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		#reload_modules()
		cssvariables.apply(view, edit)
		cssnesting.apply(view, edit)
		#print "CSS Less(ish) Compiled"

class css_less_ish_decompile_command(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		#reload_modules()
		cssnesting.remove(view, edit)
		cssvariables.remove(view, edit)
		highlight(view)
		#print "CSS Less(ish) Decompiled"

class css_less_ish_scope_command(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		regions = view.sel()
		for region in regions:
			print view.scope_name(region.a)

class css_less_ish_run_tests_command(sublime_plugin.TextCommand):
	def run(self, edit):
		reload_modules()
		reload_modules()
		tests.run(self.view, edit)

#
# Helpers
#

def highlight(view):
	highlight_delay = get_setting('highlight_delay', int)
	if highlight_delay > 0:		
		highlight_module(view, 'variables', cssvariables.highlights(view))
		highlight_module(view, 'nesting', cssnesting.highlights(view))
		callback = lambda: unhighlight(view)
		sublime.set_timeout(callback, highlight_delay)

def highlight_module(view, name, regions):
	colour = get_setting(name + '_highlight_scope', str)
	outline = get_setting(name + '_highlight_outline', bool)
	view.add_regions('css-less-ish-'+name, regions, colour, sublime.DRAW_OUTLINED if outline else sublime.DRAW_EMPTY)

def unhighlight(view):
	view.erase_regions('css-less-ish-variables')
	view.erase_regions('css-less-ish-nesting')

def get_setting(name, typeof=str):
	settings = sublime.load_settings('csslessish.sublime-settings')
	setting = settings.get(name)
	if setting:
		if typeof == str:
			return setting
		if typeof == bool:
			return setting == True
		elif typeof == int:
			return int(settings.get(name, 500))
	else:
		if typeof == str:
			return ''
		else:
			return None

def reload_modules():
	load_module('modules.cssvariables')
	load_module('modules.cssnesting')
	load_module('modules.csscolours')
	load_module('tests')
	load_module('tests.testcase')
	load_module('tests.testvariables')
	load_module('tests.testnesting')
	load_module('tests.testcolours')

# reload module (borrowed from sublimelint for ease when debugging)
basedir = os.getcwd()
def load_module(path):
	os.chdir(basedir)
	__import__(path)
	#print "Reloading "+path
	sys.modules[path] = reload(sys.modules[path])

#
# Hooks
#

class cssvariables_plugin(sublime_plugin.EventListener):
	def on_load(self, view):
		process(view, 'restore')		
	def on_pre_save(self, view):
		process(view, 'strip')		
	def on_post_save(self, view):
		process(view, 'restore')	

def process(view, type):
	if view.file_name().endswith('.css'):
		# Only process if there are variables or nestings
		if not view.find("@\w+", 0) and not view.find("\w+\s*\[", 0):
			return
		if type=='restore':
			restore_delay = get_setting('restore_delay', int)
			if restore_delay > 0:
				callback = lambda: restore(view)
				sublime.set_timeout(callback, restore_delay)
			else:
				restore(view)
		else:
			view.run_command('css_less_ish_compile')

def restore(view):
	view.run_command('css_less_ish_decompile')