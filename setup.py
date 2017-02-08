#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)
    import pip
    pip.main(['install','-r','requirements.txt'])


setup(name='transcarread',
      packages=['transcarread'],
	  install_requires=['gridaurora',
	                    'sciencedates'],
	  classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
	  ],
      dependency_links = [
      'https://github.com/scienceopen/gridaurora/tarball/master#egg=gridaurora',
      ],
	  )
