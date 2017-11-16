#!/usr/bin/env python
req = ['nose','python-dateutil', 'pytz','numpy','xarray', 'scipy',
       'gridaurora','sciencedates']
# %%
from setuptools import setup

setup(name='transcarread',
      packages=['transcarread'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/transcarrread',
      version='1.0.0',
	  classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
	  ],
	  install_requires=req,
	  python_requires='>=3.6',
      extras_require={'plot':['matplotlib','seaborn'],},
	  )
