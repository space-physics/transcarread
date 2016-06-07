#!/usr/bin/env python
import os,sys
import subprocess
from setuptools import setup 

exepath = os.path.dirname(sys.executable)
try:
    subprocess.call([os.path.join(exepath,'conda'),'install','--yes','--file','requirements.txt'])
except Exception as e:
    print('tried conda in {}, but you will need to install packages in requirements.txt  {}'.format(exepath,e))


with open('README.rst','r') as f:
	long_description = f.read()

setup(name='transcarread',
      packages=['transcarrread'],
	  description='Reading utilities for output of TRANSCAR 1-D aeronomy model',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/transcarread',
	  install_requires=['gridaurora'],
      dependency_links = ['https://github.com/scienceopen/gridaurora/tarball/master#egg=gridaurora',],
	  )
