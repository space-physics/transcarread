#!/usr/bin/env python3
"""
for reading 90kmmaxpt123.dat, which may have been generated by MSIS90
This file was figured out by inspection of dir.source/transconvec_13.op.f
Michael Hirsch
GPLv3+

inputs:
dz: altitude step

variables:
nx: number of altitudes
raw: 2-D array of data for each altitude, this is what we'll interpolate and
write back to disk

Note: by inspection, data values of 90kmmaxpt123.dat start at byte 504

TRANSCAR takes the initial conditions file as an initial state at t=0, and then
computes the state of the ionosphere for times t=0+{T1,T2,T3....Tn}.
This output is stored in dir.output/transcar_output, which is read by
read_tra.py in a similar manner to this code
"""
from __future__ import division,absolute_import
from pathlib2 import Path
import logging
from pandas import DataFrame
from numpy import fromfile, float32, arange, asarray
from datetime import datetime
from pytz import UTC
from scipy.interpolate import interp1d
#
from gridaurora.ztanh import setupz
from .isriono import compplasmaparam

d_bytes = 4
#ncol0 = 50 #from transconvec_13.op.f
headbytes = 504 #from inspection of "good" .dat file, x1F8=d504, 504 gets us up to this point

toobig = 300 #beyond which number of altitude cells transcar will crash

def readmsis(ifn, ofn, dz, newaltmethod):
    nhead = headbytes//d_bytes
    hd,hdraw = readionoheader(ifn,nhead)

    msis,raw = readinitconddat(hd,ifn) #index is altitude (km)

    pp = compplasmaparam(msis,hd['approx'])

    msisinterp,hdinterp,ppinterp, rawinterp = interpdat(msis, dz,hd,pp,raw, newaltmethod)

    writeinterpunformat(hdinterp['nx'], rawinterp,hdraw,ofn)

    return msisinterp,hdinterp,ppinterp


def getaltgrid(ifn):
    """
    Helper function for HiST-feasibility to quickly get transcar alt grid
    """
    nhead = headbytes//d_bytes
    hd = readionoheader(ifn,nhead)[0]
    msis,raw = readinitconddat(hd,ifn) #index is altitude (km)

    return msis.index.values

def interpdat(md, dz, hd, pp, raw,newaltmethod):

#%% was interpolation requested?
    if dz[0] is None:
        return md, hd, pp, raw
#%% interpolate initial conditions
    malt = newaltmethod.lower()
    if malt == 'tanh':
        z_new = setupz(md.shape[0], md.index[0], dz[0], dz[1])
    elif malt == 'linear':
        print('interpolating to grid space {:.2f}'.format(dz) + ' km.')
        z_new = arange(md.index[0], md.index[-1], dz[0], dtype=float)
    elif malt =='incr':
        """
        in this case, dz is start spacing and  amount to increase step size for each element
        The method used to implement this is inefficient, but it is a very small dataset.
        """
        z_new = [md.index[0]]
        cdz = dz[0]
        while (z_new[-1] + cdz)<md.index[-1]:
            z_new.append(z_new[-1]+cdz)
            cdz+=dz[0]
        z_new = asarray(z_new)
    else:
        logging.warning('unknown interp method {}, returning unaltered values.'.format(newaltmethod))
        return md, hd, pp, raw

    if z_new.size>toobig:
        logging.warning('note: Transcar may not accept altitude grids with more than about {} elements.'.format(toobig))



    mint = DataFrame(index=z_new,
                     columns=md.columns.values.tolist()) #this is faster than list(md)
    for m in md:
        fint = interp1d(md.index, md[m], kind='linear',axis=0)
        mint[m] = fint(z_new)
#%% new header, only change to number of altitudes
    hdint = hd
    hdint['nx'] = z_new.size
#%% raw data, we'll write this to disk later
    fint = interp1d(md.index, raw, kind='linear', axis=0)
    rawint = fint(z_new)
#%% interpolate derived parameters
    ppint = DataFrame(index=z_new,
                      columns=pp.columns.values.tolist())
    for p in pp:
        fint = interp1d(pp.index, pp[p], kind='linear', axis=0)
        ppint[p] = fint(z_new)

    return mint,hdint, ppint, rawint

def writeinterpunformat(nx, rawi, hdraw, ofn):
    if ofn is None:
        return
    ofn = Path(ofn).expanduser()
    #update header with new number of altitudes due to interpolation
    hdraw[0] = nx

    print('writing {}'.format(ofn))
    with ofn.open('wb') as f:
        hdraw.tofile(f,'','%f32')
        rawi.astype(float32).tofile(f,'','%f32')


def readionoheader(ifn, nhead):
    """ reads BINARY transcar_output file """
    ifn = Path(ifn).expanduser() #not dupe, for those importing externally
    assert ifn.is_file()

    with ifn.open('rb') as f:
        h = fromfile(f, float32, nhead)

    return parseionoheader(h), h

def parseionoheader(h):
    assert 1<=h[3]<=12
    assert 1<=h[4]<=31
    assert 0<=h[5]<24
    assert 0<=h[6]<60
    assert 0<=h[7]<60
    #... and so on with asserts. Just checking we aren't reading the totally wrong type of file
    # not a Series because all have to be same datatype
    # not a Dataframe because it's only 1-D
    hd = {'nx':h[0].astype(int), 'ncol':h[1].astype(int),
          #'year':h[2], 'month':h[3], 'day':h[4], 'hour':h[5], 'minute':h[6], 'second':h[7],
          'intpas':h[8], 'longeo':h[9], 'latgeo':h[10], 'lonmag':h[11], 'latmag':h[12],
          'tmag':h[13], 'f1072':h[14], 'f1073':h[15], 'ap2':h[16], 'ikp':h[17],
          'dTinf':h[18], 'dUinf':h[19], 'cofo':h[20], 'cofh':h[21],'cofn':h[22],
          'chi':h[23],'approx':h[36]}

    # h[37] last non-zero value till h[59], then zeros till start of data at byte 504
    # h[59] has value of 1.0

    hd['htime'] = datetime(year=h[2], month=h[3], day=h[4],
                           hour=h[5], minute=h[6], second=h[7],tzinfo=UTC)

    return hd

def readinitconddat(hd,fn):
    fn = Path(fn).expanduser()
    nx = hd['nx']
    ncol = hd['ncol']

    # *** these indices correspond exactly to the columns of msis!! ****
    # from transconvec_13.op.f lines 452 - 542
    if hd['approx'].astype(int) == 13:
        dextind = tuple(range(1,34))
    else:
        dextind = tuple(range(1,13)) + (12,13,13,14,14,15,15,16,16) + tuple(range(17,29))

    if ncol>60:
        dextind += (60,61,62)

    dextind += (49,) #as in output

    with fn.open('rb') as f: #python2 requires r first
        ipos = 2* ncol *d_bytes
        f.seek(ipos,0)
        rawall = fromfile(f,float32,nx*ncol).reshape((nx,ncol),order='C') #yes order='C'!

    msis = DataFrame(rawall[:,dextind],
                     index = rawall[:,0], # altitude
                     columns=('n1','n2','n3','n4','n5','n6',
                              'v1','v2','v3','vm','ve',
                              't1p','t1t','t2p','t2t','t3p','t3t',
                              'tmp','tmt','tep','tet',
                              'q1','q2','q3','qe','nno','uno',
                              'po','ph','pn','pn2','po2','heat',
                              'po1d','no1d','uo1d','n7'))

    return msis,rawall
#%% plots
def doplot(d, pp, ifn):

    figure(1).clf()
    ax= figure(1).gca()
    for i in ['n'+str(j) for j in range(1,7)]:
        ax.plot(d[i], d.index, label=i)

    ax.set_xscale('log')
    ax.legend(loc='best')
#    #msis.plot(y='alt',x='n4',title=ifn,logx=True) # why doesn't this plot correctly?
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('n')
    ax.set_title('density')

    figure(2).clf()
    a2= figure(2).gca()
    for s in ('v1','v2','v3','ve','vm'):
        a2.plot(d[s], d.index, label=s)
    a2.set_xlabel('v')
    a2.set_ylabel('altitude [km]')
    a2.legend(loc='best')
    a2.grid(True)

    plotisr(pp, 10,(None,None),ifn)
    plotisr(pp, 11,(90,300),ifn)

def plotisr(pp,fgn,zlim,ifn):
    bn = Path(ifn).name
    figure(fgn).clf()

    fg,ax = subplots(nrows=1,ncols=3,sharey=True, num=fgn, figsize=(12,5))
    ax[0].plot(pp['ne'], pp.index)
    ax[0].set_xlabel('$n_e$')
    ax[0].set_ylabel('alt [km]')
    ax[0].set_xscale('log')

    ax[1].plot(pp['vi'], pp.index)
    ax[1].set_xlabel('$v_i$')
    ax[1].set_title(bn,y=1.05)


    ax[2].plot(pp['Ti'], pp.index, label='$T_i$')
    ax[2].plot(pp['Te'], pp.index, label='$T_e$')
    ax[2].set_xlabel('Temperature')
    ax[2].legend(loc='best')

    for a in ax:
        a.set_ylim(zlim)
        a.grid(True)

#    #fg.tight_layout() #no, it spaces the subplots wider
    fg.subplots_adjust(wspace=0.075) #brings subplots horizontally closer

if __name__ == '__main__':
    from matplotlib.pyplot import figure,show, subplots
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

    doplot(msisi, ppi,a.infn)
    show()
