import sublime
from tests.testvariables import TestVariables
from tests.testnesting import TestNesting
from tests.testcolours import TestColours

def run(view, edit):
	view, edit = create_new_view(view)
	output = "CSS LESS(ish) UNIT TESTS\n" + "=" * 50 + "\n"
	tests = [
		TestVariables(view, edit), 
		TestNesting(view, edit), 
		TestColours(view, edit)
		]
	for test in tests:
		output+= get_test_output( test )
	for test in tests:
		output+= get_test_errors( test )
	view.replace(edit, sublime.Region(0, view.size()), '')
	view.insert(edit, 0, output)
	close_view(view, edit)
	highlight(view)

def highlight(view):
	# OK regions
	regions = view.find_all('\.')
	#view.add_regions('css-less-ish-ok', regions, 'entity.name.class', sublime.DRAW_EMPTY) # sublime.DRAW_OUTLINED if outline else 
	# Error regions
	regions = view.find_all('N')
	add = []
	for region in regions:
		line = view.line(region)
		if view.substr(line).find('(') > 0 and view.rowcol(line.a)[0] > 0:
			add.append(region)
	view.add_regions('css-less-ish-error', add, 'storage', sublime.DRAW_EMPTY) # sublime.DRAW_OUTLINED if outline else 
	#callback = lambda: unhighlight(view)
	#sublime.set_timeout(callback, 1000)
					
def unhighlight(view):
	view.erase_regions('css-less-ish-ok')
	view.erase_regions('css-less-ish-error')

def create_new_view(view):
	view = sublime.active_window().new_file()
	#view.set_syntax_file('Packages/CSS/CSS.tmLanguage')
	edit = view.begin_edit()
	return view, edit

def close_view(view, edit):
	view.end_edit(edit)

def get_test_output(test):
	output = test.setup()
	output+= test.run()
	return output

def get_test_errors(test):
	errors = test.errors
	if len(errors)> 0:
		return ' -' + '\n -'.join(errors)
	return ''



