#!/usr/bin/env python

import glob
import os

"""
Generate the code documentation, using pydoc.
"""

for dirname in ['simulaciodades', 'simulacioparking', 'clusteringsklearn', 'clusteringpytorch', 'api']:
	flist = glob.glob('%s/*.py' % dirname)
	for fname in flist:
		if '__init__' not in fname:
			print(fname)
			os.system('python -m pydoc -w %s' % fname)
			bname = os.path.splitext(os.path.basename(fname))[0]  # eg 'smartbox'
			os.system('mv %s.html %s.%s.html' % (bname, dirname, bname))
	os.system('python -m pydoc -w %s' % dirname)
os.system('mv *.html docs')
