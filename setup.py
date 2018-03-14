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
      long_description=open('README.rst').read(),
      description='read and plot Transcar 1-D particle precipitation ionospheric model.',
      version='1.1.0',
	  classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
	  ],
	  install_requires=install_requires,
	  tests_require=tests_require,
	  python_requires='>=3.6',
      extras_require={'plot':['matplotlib','seaborn'],
                      'tests':tests_require,},
      scripts=['PlotTranscarInput.py','transcar2isr.py','transcar2excitationrates.py'],
	  )
