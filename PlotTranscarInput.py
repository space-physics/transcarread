#!/usr/bin/env python
"""
Reads Transcar inputs and MSIS90 and plots interpolated result that would 
normally go into Transcar.
"""
from matplotlib.pyplot import show
#
from transcarread import readmsis
from transcarread.plots import plotionoinit



if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='reads, and optionally interpolates and rewrites MSIS90 initial conditions data')
    p.add_argument('-i','--infn',help='input filename',type=str,default='~/code/transcar/dir.transcar.server/dir.input/90kmmaxpt123.dat')
    p.add_argument('-o','--outfn',help='output filename',type=str,default=None)
    p.add_argument('-d','--dz',help='new z altitude grid spacing to interpolate to  (for tanh, (dzmin,dzmax))',type=float,nargs='+',default=[None])
    p.add_argument('-m','--newaltmethod',help='method of generating new altitude cell locations [linear, incr]',type=str,default='linear')
    a = p.parse_args()

    #tic = time()
    msisi,hdi,ppi = readmsis(a.infn,a.outfn, a.dz,a.newaltmethod)
    #print('read ' + a.infn + ' in {:0.2f}'.format(1000*(time()-tic)) + ' ms.')
    print('initial conditions from ' + str(hdi['htime']) + ' at lat,lon ' +
           str(hdi['latgeo']) +', '+ str(hdi['longeo']))

    print('nx={:0d}'.format(hdi['nx']) + ' from {:0.2f}'.format(msisi.index[0]) +
          ' km to {:0.2f}'.format(msisi.index[-1]) + ' km.')

    plotionoinit(msisi, ppi,a.infn)
    show()
