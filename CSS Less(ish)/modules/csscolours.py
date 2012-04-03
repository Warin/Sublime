import colorsys

#
# Colour functions
#


# lighten(@color, 10%);     // return a color which is 10% *lighter* than @color
# darken(@color, 10%);      // return a color which is 10% *darker* than @color
# saturate(@color, 10%);    // return a color 10% *more* saturated than @color
# desaturate(@color, 10%);

def lighten(colour, percent_str):
	h,s,v = hex_to_hsv(colour)
	percent = _format_percent(percent_str)
	if v < 1: 
		v = v + (percent * v)	# try value first
	else:
		s = s - (percent * s)	# or decrease saturation
	return hsv_to_hex(h,s,v)

def darken(colour, percent_str):
	h,s,v = hex_to_hsv(colour)
	percent = _format_percent(percent_str)
	v = v - (percent * v)
	return hsv_to_hex(h,s,v)

def saturate(colour, percent_str):
	h,s,v = hex_to_hsv(colour)
	percent = _format_percent(percent_str)
	s = s + (percent * s)
	v = v + (percent * v)
	return hsv_to_hex(h,s,v)

def desaturate(colour, percent_str):
	h,s,v = hex_to_hsv(colour)
	percent = _format_percent(percent_str)
	s = s - (percent * s)
	v = v - (percent * v)
	return hsv_to_hex(h,s,v)

#
# 
#

def hex_to_hsv(colour):
	colour = colour.replace('#', '')
	if len(colour) == 3:
		colour = colour[0]+colour[0]+colour[1]+colour[1]+colour[2]+colour[2]
	if len(colour) != 6:
		return None
	r,g,b  = rgb(colour)
	r,g,b  = rgb_to_percentage(r,g,b)
	h,s,v  = colorsys.rgb_to_hsv(r,g,b)
	return (h,s,v)

def hsv_to_hex(h, s, v):
	s,v       = min(s, 1), min(v, 1)
	r,g,b     = colorsys.hsv_to_rgb(h,s,v)
	r,g,b     = percentage_to_rgb(r,g,b)
	hexcolour = '#%02x%02x%02x' % (r,g,b)
	return hexcolour

#
# Helpers
#

def _format_percent(percent):
	if not isinstance(percent, float):
		percent = float(percent.replace('%', ''))
	if percent > 1:
		percent = percent/100
	#value = min(percent * value, 1)
	return percent

def rgb(triplet):
	triplet = triplet.lower()
	HEX = '0123456789abcdef'
	return (HEX.index(triplet[0])*16 + HEX.index(triplet[1]),
				HEX.index(triplet[2])*16 + HEX.index(triplet[3]),
				HEX.index(triplet[4])*16 + HEX.index(triplet[5]))

def rgb_to_percentage(r,g,b):
	return r/255.0, g/255.0, b/255.0

def percentage_to_rgb(r,g,b):
	return r*255.0, g*255.0, b*255.0