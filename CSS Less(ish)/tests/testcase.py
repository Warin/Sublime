import sublime
import inspect
from modules import cssvariables 

class TestCase():

	output = ''
	errors = []
	
	def __init__(self, view, edit):
		self.output = ''
		self.errors = []
		self.view = view
		self.edit = edit

	def setup(self):
		return "\nRunning " + self.title + "\n" + "-" * 50 + "\n"

	def run(self):
		methods = self.get_test_methods()
		for testname in methods:
			self.output+= ''+ testname + '() '
			eval('self.'+testname+'()')
			self.output+= '\n'
		return self.output

	def teardown():
		pass

	def get_test_methods(self):
		test_methods = []
		members = inspect.getmembers(self, predicate=inspect.ismethod)
		for name, func in members:
			if name.find("test_") == 0:
				test_methods.append(name)
		return test_methods

	def set_text(self, text):
		self.view.replace(self.edit, sublime.Region(0, self.view.size()), '')
		self.view.insert(self.edit, 0, text)
	
	def compile(self):
		self.view.run_command('css_less_ish_compile')	

	def decompile(self):
		self.view.run_command('css_less_ish_decompile')	

	def get_variables_dict(self):
		return cssvariables.get_css_variables_dict(self.view)

#
#
#

	def error(self, text):
		self.errors.append(text)
		self.output+= 'N'

	def ok(self):
		self.output+= '.'

#
#
#

	def variable_equals(self, varname, value):
		variables = self.get_variables_dict()
		if not varname in variables:
			self.error( "\nVariable @"+ varname +" does not exist\n" )
		elif variables[varname] != value:
			self.error( "\nValue of @"+varname+": " + variables[varname] + " != " + value + '\n')
		else:
			self.ok()

	def text_equals(self, sent):
		text = self.view.substr(sublime.Region(0, self.view.size()))
		if text.strip() != sent.strip():
			self.error( 'text_equals' )
		else:
			self.ok()

	def find(self, text):
		match = self.view.find(text, 0)
		if match:
			self.ok()
		else:
			self.error( "Couldn't find \""+ text + "\"" )