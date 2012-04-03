import testcase
import modules.csscolours as colour

class TestColours(testcase.TestCase):

	title = "CSS Colours"
	basecolour = "#456"

	def test_colours(self):
		self.set_text( self.text() )
		self.compile()
		# check variables exist with correct values
		self.variable_equals('lighter', colour.lighten(self.basecolour, .2))
		self.variable_equals('darker', colour.darken(self.basecolour, .2))
		self.variable_equals('saturated', colour.saturate(self.basecolour, .2))
		self.variable_equals('desaturated', colour.desaturate(self.basecolour, .2))
		# check variables have been swapped in
		self.find('lighter: '+ colour.lighten(self.basecolour, .2) +';')
		self.find('darker: '+ colour.darken(self.basecolour, .2) +';')
		self.find('saturated: '+ colour.saturate(self.basecolour, .2) +';')
		self.find('desaturated: '+ colour.desaturate(self.basecolour, .2) +';')
		# check restoring resets variables
		self.decompile()
		self.find('lighter: @lighter;')
		self.find('darker: @darker;')
		self.find('saturated: @saturated;')
		self.find('desaturated: @desaturated;')

	def text(self):
		return """
/*
* @colour = """+self.basecolour+"""
* @lighter = lighten( @colour , 20%)
* @darker = darken( @colour, .2 )
* @saturated= saturate  ( @colour, .2 )
* @desaturated=desaturate ( @colour , .2 )
*/

a {lighter: @lighter;}
a {darker: @darker;}
a {saturated: @saturated;}
a {desaturated: @desaturated;}

"""