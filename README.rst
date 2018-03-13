.. image:: https://travis-ci.org/scivision/transcarread.svg?branch=master
    :target: https://travis-ci.org/scivision/transcarread

.. image:: https://coveralls.io/repos/github/scivision/transcarread/badge.svg?branch=master
    :target: https://coveralls.io/github/scivision/transcarread?branch=master
    
.. image:: https://ci.appveyor.com/api/projects/status/um51akgrwe2uogla?svg=true
    :target: https://ci.appveyor.com/project/scivision/transcarread

.. image:: https://api.codeclimate.com/v1/badges/67284a35127f7ea3beea/maintainability
   :target: https://codeclimate.com/github/scivision/transcarread/maintainability
   :alt: Maintainability


=============
transcar-read
=============

Reads the output of the `TRANSCAR <https://github.com/scivision/transcar>`_ 1-D particle penetration ionosphere model.


Install
=======

`Python <https://conda.io/miniconda.html>`_ >= 3.6 required::

    python -m pip install -e .
    
Usage
=====

* transcar2aurora.py: Generate simulated auroral emissions based on Transcar excitation rates.
* transcar2isr.py: Generate simulated Incoherent Scatter Radar plasma paremters based on Transcar sim.
* transcar2excitationradar.py: plots excitation rates output by Transcar sim.
* PlotTranscarInput.py: plots interpolated transcar inputs (MSIS90).

