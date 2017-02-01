#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)


setup(name='transcarread',
      packages=['transcarread'],
	  install_requires=['gridaurora','histutils'],
      dependency_links = [
      'https://github.com/scienceopen/gridaurora/tarball/master#egg=gridaurora',
      'https://github.com/scienceopen/histutils/tarball/master#egg=histutils'],
	  )
