#!/usr/bin/env python3

from setuptools import setup 

with open('README.rst') as f:
	long_description = f.read()
	
setup(name='transcarread',
      version='0.1',
	  description='Reading utilities for output of TRANSCAR 1-D aeronomy model',
	  long_description=long_description,
	  author='Michael Hirsch',
	  author_email='hirsch617@gmail.com',
	  url='https://github.com/scienceopen/transcarread',
	  install_requires=['numpy','pytz','pandas','scipy'],
      packages=['transcarread'],
	  )
