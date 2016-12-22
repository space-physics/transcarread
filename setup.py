#!/usr/bin/env python
import subprocess
from setuptools import setup

try:
    subprocess.call(['conda','install','--file','requirements.txt'])
except Exception as e:
    pass



setup(name='transcarread',
      packages=['transcarread'],
	  description='Reading utilities for output of TRANSCAR 1-D aeronomy model',
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/transcarread',
	  install_requires=['gridaurora','histutils'],
      dependency_links = [
      'https://github.com/scienceopen/gridaurora/tarball/master#egg=gridaurora',
      'https://github.com/scienceopen/histutils/tarball/master#egg=histutils'],
	  )
