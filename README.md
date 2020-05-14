# Transcar Read

[![image](https://travis-ci.org/space-physics/transcarread.svg?branch=master)](https://travis-ci.org/space-physics/transcarread)
[![PyPi version](https://img.shields.io/pypi/pyversions/transcarread.svg)](https://pypi.python.org/pypi/transcarread)
[![PyPi Download stats](http://pepy.tech/badge/transcarread)](http://pepy.tech/project/transcarread)

Reads the output of the
[TRANSCAR](https://github.com/space-physics/transcar) 1-D particle
penetration ionosphere model.

## Install

```sh
pip install -e .
```

## Usage

These scripts plot Transcar simulation results

* optimal_emission.py: Generate simulated auroral emissions based on Transcar excitation rates.
* plasma_state.py: Plot simulated Incoherent Scatter Radar plasma paremters from Transcar sim. These plots are over the time range of the simulation (seconds, hours, etc.)
* excitation_rates.py: plots excitation rates output by Transcar sim.
* PlotTranscarInput.py: plots interpolated transcar inputs (MSIS90).
