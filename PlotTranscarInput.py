#!/usr/bin/env python
"""
Reads Transcar inputs and MSIS90 and plots interpolated result that would
normally go into Transcar.

example:
python PlotTranscarInput.py tests/data/beam52/dir.input/90kmmaxpt123.dat
"""
from matplotlib.pyplot import show
#
import transcarread as tr
import transcarread.plots as plots



if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='reads, and optionally interpolates and rewrites MSIS90 initial conditions data')
    p.add_argument('infn',help='input filename')
    p.add_argument('-o','--outfn',help='output filename')
    p.add_argument('-d','--dz',help='new z altitude grid spacing to interpolate to  (for tanh, (dzmin,dzmax))',type=float,nargs='+')
    p.add_argument('-m','--newaltmethod',help='method of generating new altitude cell locations [linear, incr]',default='linear')
    p = p.parse_args()

    msis = tr.readmsis(p.infn, p.outfn, p.dz, p.newaltmethod)

    hd = msis.attrs['hd']

    print('initial conditions from', hd['htime'],'at lat,lon',hd['latgeo'],hd['longeo'])
    print(f'nx={hd["nx"]:0d}  from {msis.alt_km[0].item():0.1f} km to {msis.alt_km[-1].item():0.1f}  km.')

    plots.plotionoinit(msis['msis'])
    plots.plotisrparam(msis['pp'])

    show()
