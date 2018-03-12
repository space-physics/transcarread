#!/usr/bin/env python
install_requires = ['python-dateutil', 'pytz','numpy','xarray', 'scipy',
       'gridaurora','sciencedates']
tests_require=['pytest','nose','coveralls']
# %%
from setuptools import setup,find_packages

setup(name='transcarread',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/transcarrread',
      version='1.0.1',
	  classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
	  ],
	  install_requires=install_requires,
	  tests_require=tests_require,
	  python_requires='>=3.6',
      extras_require={'plot':['matplotlib','seaborn'],
                      'tests':tests_require,},
	  )
