import sublime
import re
import modules.csscolours as colour

#
# Primary functions
#

def apply(view, edit):
	cache = get_region_cache(view)
	if cache:
		return
	remove_region_cache(view, edit)
	trim_entire_content(view, edit)
	append_region_cache(view, edit)

def remove(view, edit):
	apply_region_cache(view, edit)
	remove_region_cache(view, edit)

def highlights(view):
	return view.find_all("@(\w|-)+")

#
# Content functions
#

region_cache_name = "Variables"

# Returns dictionary of variables a.  Finds a match of _@varname = "value"_ rather than looking specifically within comments (ie assumes variable names DONT have = usually)
def get_css_variables_dict(view):
	# str_hex = '7EBB43'
	# str_hex = '5CBB00'
	# #str_hex = 'ff0000'
	# #str_hex = '111111'
	# print str_hex
	# print 'lighten is '+ colour.lighten(str_hex, '50%')
	# print 'darken is '+ colour.darken(str_hex, '50%')
	# print 'saturate is '+ colour.saturate(str_hex, '50%')
	# print 'desaturate is '+ colour.desaturate(str_hex, '50%')

	# match all @var = "value", or @var='value' or @var-name = 'value'
	#matches = view.find_all("@(\w|-)+\s?+=\s?+(\"|\')[^(\"|\')]+(\"|\')",0) # this one only looks for quote marks
	value = r"'|\"|#|\w|\(|\)|@|,| |=|%|\.|-|:|;|\+|\*|\/[^\/]" # variable "value" match
	matches = view.find_all("@(\w|-)+?(\s+)?=\s?+("+value+")+",0) 
	d = {}
	#print view.substr(matches)
	for match in matches:
		# grab the actual text matched @var = "val" and split up
		text = view.substr(match)
		varname,value = text.split("=", 1)
		# format variable name text
		varname = varname.replace('@', '').strip()
		# format value text
		value = value.strip()
		if value.endswith('"') or value.endswith("\'"): # previously removed all " and ' chars - now just strip them from the front and end
			value = value[:-1]
		if value.startswith('"') or value.startswith("\'"): 
			value = value[1:]
		# value = value.replace('\"', '').replace("\'", '').strip()
		# add to dictionary
		d[varname] = value.strip()
	# calculate values
	for varname in d:
		value = d[varname]
		if value.find('@')>=0 or value.find('(')>=0:
			d[varname] = calculate_value(value, d)
	return d

def calculate_value(value, d):
	# Substitute in variables
	for varname in d:
		if varname in value:
			value = value.replace('@'+varname, d[varname])
	# look for numeric values (to do maths on them)
	numeric = value.replace('px', '')
	match = re.match(r'([0-9]| |\+|\-|\*)+', numeric)
	if match:
		try:
			value = str(eval(numeric)) + 'px'
		except:
			pass
	# look for function
	match = re.search(r'(\w+)\s*?\((.*?),(.*)\)', value)
	if match:
		func = match.group(1)
		var1 = match.group(2).strip()
		var2 = match.group(3).strip()
		if func in ('lighten', 'darken', 'saturate', 'desaturate'):
			value = eval('colour.'+ func + '("' + var1 + '","' + var2 + '")')
	return value

def get_first_comment(view):
	return view.find(r"\/\*+(\*|\w|\W)*?\*\/",0)  # better

def trim_entire_content(view, edit):
	while True:
		line_region = view.line(view.size())
		line = view.substr(line_region).strip()
		if line == '':
			view.replace(edit, sublime.Region(line_region.a - 1, line_region.b), '')
		else:	
			break;

#
# Region cache functions
#

def get_region_cache(view):
	return view.find("\/\*+\s?+"+region_cache_name +"[^\*\/]*\*\/", 0) 

def remove_region_cache(view, edit):
	region = get_region_cache(view)
	if region:
		view.replace(edit, region, '')
	return

# Converts variables to their values and appends region indexes to the bottom (to be parsed later)
def append_region_cache(view, edit):
	variables = get_css_variables_dict(view)
	docblock = get_first_comment(view)
	if not docblock:
		print "No first comment found"
		return
	# Loop through region matches (outside of the docblock)
	offset = docblock.b
	match = view.find("@(\w|-)+", offset)
	pos = {} # assoc array of a:b string pairs
	highlight = []
	for varname in variables:
		pos[varname] = []
	while match:
		varname = view.substr(match).replace('@', '')
		scope_name = view.scope_name(match.a)
		if varname in variables and scope_name.find('comment')==-1:
			# and not 'comment' in scope_name:
			value = variables[varname]
			view.replace(edit, match, value)
			offset = match.a + len(value)
			pos[varname].append(str(match.a) + ":" + str(offset))	# store in pos dict
			highlight.append( sublime.Region(match.a, offset) )	# store replaced region for highlighting
		else:
			offset+=1
		match = view.find("@(\w|-)+", offset)	# go again
	# Compile the output	
	output = []
	for varname in variables:
		if pos[varname]:
			output.append ( varname +"{" + ','.join( pos[varname] ) + "}" )
	if len(output) > 0:
		cache = "/* " + region_cache_name + ":"
		cache+= '.'.join(output)
		cache+= " */"
		view.insert(edit, view.size(), "\n\n"+cache)
	return highlight

# Returns cache regions as array[varname] = [ [n,n], [n,n] ]
def parse_region_cache(view):
	region = get_region_cache(view)
	if not region:
		#print "No region cache found"
		return
	cache = view.substr( get_region_cache(view) )
	cache = cache.replace('/* '+region_cache_name+':', '').replace(' */', '')
	regions = {}
	# Break into section
	sections = cache.split('.')
	for section in sections:
		varname, data = section.split('{')
		data = data.replace('}', '')
		pos = data.split(',') 	# array of n:n, n:n
		regions[varname] = []	# empty list for each variable key
		for pair in pos:
			a, b = pair.split(':')	
			regions[varname].append([int(a), int(b)])
	return regions

# Uses parsed region cache to re-apply the variable names within the content
def apply_region_cache(view, edit):
	data = {}		# assoc array with key 'a' as position index - storing 'varname' and related 'b' value
	ordering = []	# ordered array by a region's 'a' index
	parsed = parse_region_cache(view)
	if parsed:
		# Create data and ordering objects
		for varname in parsed:
			for pos in parsed[varname]:
				data[pos[0]] = {'varname':varname, 'b':pos[1]}
				ordering.append(pos[0])
		# sort and reverse ordering - replacing regions from bottom to top 
		ordering.sort()
		for a in reversed(ordering):
			b = data[a]['b']
			varname = data[a]['varname']
			view.replace(edit, sublime.Region(a, b), '@'+varname)
		# # highlight from top to bottom - accounting for 'shifting' regions during above replacement
		# diff = 0	
		# for a in ordering:
		# 	b = data[a]['b']
		# 	varname = data[a]['varname']
		# 	highlights.append(sublime.Region(diff + a, diff + a + len('@'+varname)))	
		# 	diff+= len('@'+varname) - (b-a)