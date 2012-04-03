import testcase

class TestNesting(testcase.TestCase):

	title = "CSS Nesting"

	def test_nestings(self):
		self.set_text( self.input() )
		self.text_equals( self.input() )
		self.compile()
		self.text_equals( self.result() )
		self.decompile()
		self.text_equals( self.input() )

	def input(self):
		return """
	.header [
		h1 {}
		.title {} /* Comment */
	]
"""

	def result(self):
		return """
	/*.header [*/
		.header h1 {}
		.header .title {} /* Comment */
	/*]*/
"""
