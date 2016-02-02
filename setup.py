#!/usr/bin/env python3

from setuptools import setup 

with open('README.rst','r') as f:
	long_description = f.read()
	
setup(name='transcarread',
      version='0.1',
	  description='Reading utilities for output of TRANSCAR 1-D aeronomy model',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/transcarread',
	  install_requires=['gridaurora']
      dependency_links = ['https://github.com/scienceopen/gridaurora/tarball/master#egg=gridaurora',],
      packages=['transcarread'],
	  )
