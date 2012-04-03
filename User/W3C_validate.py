import os
import sublime
import sublime_plugin


class ValidateCommand(sublime_plugin.TextCommand):
	'''
	This plugin is dependent on /User/w3c-validator.py, which you can get from here:
	https://github.com/srackham/w3c-validator
	'''
	def run(self, edit):
		if len(self.view.file_name()) > 0 and self.view.file_name().endswith((".html", ".css")):
			folder_name, file_name = os.path.split(self.view.file_name())
			self.view.window().run_command('exec', {'cmd': ['python', sublime.packages_path() + "\User\w3c-validator.py", file_name], 'working_dir': folder_name})
			sublime.status_message(("Validating %s...") % file_name)

	def is_enabled(self):
		return self.view.file_name() and len(self.view.file_name()) > 0
