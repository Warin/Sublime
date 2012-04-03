#!/usr/bin/env python
'''
w3c-validator - Validate HTML and CSS files using the WC3 validators

Copyright: Stuart Rackham (c) 2011
License:   MIT
Email:     srackham@gmail.com
'''

import os
import sys
import time
import json
import commands
import urllib

html_validator_url = 'http://validator.w3.org/check'
css_validator_url = 'http://jigsaw.w3.org/css-validator/validator'

verbose_option = False

def message(msg):
	print >> sys.stderr, msg

def verbose(msg):
	if verbose_option:
		message(msg)

def validate(filename):
	'''
	Validate file and return JSON result as dictionary.
	'filename' can be a file name or an HTTP URL.
	Return '' if the validator does not return valid JSON.
	Raise OSError if curl command returns an error status.
	'''
	quoted_filename = urllib.quote(filename)
	if filename.startswith('http://'):
		# Submit URI with GET.
		if filename.endswith('.css'):
			cmd = ('curl -sG -d uri=%s -d output=json -d warning=0 %s'
					% (quoted_filename, css_validator_url))
		else:
			cmd = ('curl -sG -d uri=%s -d output=json %s'
					% (quoted_filename, html_validator_url))
	else:
		# Upload file as multipart/form-data with POST.
		if filename.endswith('.css'):
			cmd = ('curl -F "file=@%s;type=text/css" -F output=json -F warning=0 %s'
					% (quoted_filename, css_validator_url))
		else:
			cmd = ('curl -F "uploaded_file=@%s;type=text/html" -F output=json %s'
					% (quoted_filename, html_validator_url))
	verbose(cmd)
	status,output = commands.getstatusoutput(cmd)
	if status != 0:
		print(output)
		raise OSError (status, 'failed: %s' % cmd)
	verbose(output)
	try:
		result = json.loads(output)
	except ValueError:
		result = ''
	time.sleep(2)   # Be nice and don't hog the free validator service.
	return result


if __name__ == '__main__':
	if len(sys.argv) >= 2 and sys.argv[1] == '--verbose':
		verbose_option = True
		args = sys.argv[2:]
	else:
		args = sys.argv[1:]
	if len(args) == 0:
		message('usage: %s [--verbose] FILE|URL...' % os.path.basename(sys.argv[0]))
		exit(1)
	errors = 0
	warnings = 0
	for f in args:
		message('validating: %s ...' % f)
		retrys = 0
		while retrys < 2:
			result = validate(f)
			if result:
				break
			retrys += 1
			message('retrying: %s ...' % f)
		else:
			message('failed: %s' % f)
			errors += 1
			continue
		if f.endswith('.css'):
			errorcount = result['cssvalidation']['result']['errorcount']
			warningcount = result['cssvalidation']['result']['warningcount']
			errors += errorcount
			warnings += warningcount
			if errorcount > 0:
				message('errors: %d' % errorcount)
			if warningcount > 0:
				message('warnings: %d' % warningcount)
		else:
			for msg in result['messages']:
				if 'lastLine' in msg:
					message('%(type)s: line %(lastLine)d: %(message)s' % msg)
				else:
					message('%(type)s: %(message)s' % msg)
				if msg['type'] == 'error':
					errors += 1
				else:
					warnings += 1
	if errors:
		exit(1)
