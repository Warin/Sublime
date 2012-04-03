import testcase

class TestVariables(testcase.TestCase):

	title = "CSS Variables"

	def test_variables(self):
		self.set_text( self.variables_text() )
		self.compile()
		# check variables exist with correct values
		self.variable_equals('var1', 'val1')
		self.variable_equals('var2', 'val2')
		self.variable_equals('var3', 'val3')
		self.variable_equals('var4', 'val1')	# referenced
		self.variable_equals('var5', '/../../path')
		# Tricky stuff
		self.variable_equals('filter', "filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#f6f6f6',GradientType=0 );")
		self.variable_equals('filter2', 'filter: progid:DXImageTransform.Microsoft.gradient( startColorstr="#ffffff", endColorstr="#f6f6f6",GradientType=0 )')
		# check variables have been swapped in
		self.find('colour1: val1;')
		self.find('colour2: val2;')
		self.find('colour3: val3;')
		self.find('colour4: val1;')
		# check restoring resets variables
		self.decompile()
		self.find('colour1: @var1;')
		self.find('colour2: @var2;')
		self.find('colour3: @var3;')
		self.find('colour4: @var4;')

	def test_numeric_variables(self):
		self.set_text( self.numeric_variables_text() )
		self.compile()
		self.find('width: 34px;')
		self.find('height: 32px;')


	def variables_text(self):
		return """
/*
* @var1 =  "val1" // Comment
* @var2 ='val2'
* @var3= val3 
* @var4 =  @var1 // Variable reference
* @var5    	=  /../../path // Path with comment too
* @filter  = filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#f6f6f6',GradientType=0 );
* @filter2  = filter: progid:DXImageTransform.Microsoft.gradient( startColorstr="#ffffff", endColorstr="#f6f6f6",GradientType=0 )
*/

h1 { colour1: @var1;/* comment */}
h2 { colour2: @var2;// comment}
h3 { colour3: @var3;}
h4 { colour4: @var4;}
img{src:@var5;}

"""

	def numeric_variables_text(self):
		return """
/*
* @var1 = 12px
* @var2 = 2px
* @var3 = 10px
* @var4 = @var1*@var2-@var3+20
* @var5 = @var1 * @var2 - @var3 + 20 - 2
*/

div {width: @var4; height: @var5;}

"""

