#!/usr/bin/env python
from setuptools import setup

req = ['nose','python-dateutil','pytz','numpy','xarray','scipy','matplotlib','seaborn',
        'gridaurora','sciencedates']


setup(name='transcarread',
      packages=['transcarread'],
	  install_requires=req,
	  classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
	  ],
	  )
