#!/usr/bin/env python
from . import Path
from datetime import datetime
from numpy import fromfile,float32, empty
from xarray import DataArray
from matplotlib.pyplot import figure
from matplotlib.dates import MinuteLocator, SecondLocator, DateFormatter
from matplotlib.colors import LogNorm
#
from .readionoinit import parseionoheader, readionoheader
from .readTranscar import picktime
from .isriono import compplasmaparam
"""
reads binary "transcar_output" file
many more quantities exist in the binary file, these are the ones we use so far.
requires: Matplotlib >= 1.4

examples: test_readtra.py

Michael Hirsch

inputs:
tcofn: path/filename of transcar_output file
tReq: optional, datetime at which to extract data from file (will still read whole file first)

variables:
n_t: number of time steps in file
n_alt: number of altitudes in simulation
d_bytes: number of bytes per data element
size_record: number of data bytes per time step

Note: header length = 2*ncol
"""
nhead = 126 #a priori from transconvec_13
d_bytes = 4 # a priori
ISRPARAM = ['ne','vi','Ti','Te']
PARAM = ['n1','n2','n3','n4','n5','n6','n7',
            'v1','v2','v3','vm','ve',
            't1p','t1t','t2p','t2t','t3p','t3t','tmp','tmt','tep','tet']

def read_tra(tcofn,tReq=None):
    head0 = readionoheader(tcofn, nhead)[0]
    ncol = head0['ncol']; n_alt = head0['nx']

    size_head = 2*ncol #+2 by defn of transconvec_13
    size_data_record = n_alt*ncol #data without header
    size_record = size_head + size_data_record

    assert size_head == nhead
#%% read data based on header
    iono,chi,pp = loopread(tcofn,size_record,ncol,n_alt,size_head,size_data_record,tReq)

    return iono,chi, pp

def loopread(tcoutput,size_record,ncol,n_alt,size_head,size_data_record,tReq):
    tcoutput = Path(tcoutput).expanduser()
    n_t = tcoutput.stat().st_size//size_record//d_bytes

    chi  = empty(n_t,float)
    t =    empty(n_t,datetime)

    plasmaparam = DataArray(data=empty((n_t,n_alt,4)),
                            dims=['time','alt_km','isrparam'])
    iono = DataArray(data=empty((n_t,n_alt,22)),
                     dims=['time','alt_km','param'])

    with tcoutput.open('rb') as f: #reset to beginning
        for i in range(n_t):
            iono[i,...], chi[i], t[i], alt, plasmaparam[i,...] = data_tra(f, size_record,ncol,n_alt, size_head, size_data_record)
        # FIXME isn't there a way to inherit coordinates like Pandas?
        iono = iono.assign_coords(time=t,param=PARAM,alt_km=alt)
        plasmaparam = plasmaparam.assign_coords(time=t,isrparam=ISRPARAM,alt_km=alt)
#%% handle time request -- will return Dataframe if tReq, else returns Panel of all times
    if tReq is not None: #have to qualify this since picktime default gives last time as fallback
        tUsedInd = picktime(iono.time, tReq, None)[0]
        if tUsedInd is not None: # in case ind is 0
            iono = iono[tUsedInd,...]
            plasmaparam = plasmaparam[tUsedInd,...]

    return iono,chi,plasmaparam

def data_tra(f, size_record, ncol, n_alt, nhead, size_data_record):
#%% parse header
    h = fromfile(f, float32, nhead)
    head = parseionoheader(h)
#%% read and index data
    data = fromfile(f,float32,size_data_record).reshape((n_alt,ncol),order='C')

    dextind = tuple(range(1,7)) + (49,) + tuple(range(7,13))
    if head['approx'] >= 13:
        dextind += tuple(range(13,22))
    else:
        dextind += (12,13,13,14,14,15,15,16,16)
    #n7=49 if ncol>49 else None

    iono = DataArray(data[:,dextind],
                     coords=[('alt_km',data[:,0]),
                           ('isrparam', PARAM)])
#%% four ISR parameters
    """
    ion velocity from read_fluidmod.m
    data_tra.m does not consider n7 for ne or vi computation,
    BUT read_fluidmod.m does consider n7!
    """
    pp = compplasmaparam(iono,head['approx'])

    return iono, head['chi'],head['htime'], data[:,0],pp

def timelbl(time,ax,tctime):
    if time.size<200:
        ax.xaxis.set_minor_locator(SecondLocator(interval=10))
        ax.xaxis.set_minor_locator(SecondLocator(interval=2))
    elif time.size<500:
        ax.xaxis.set_minor_locator(MinuteLocator(interval=10))
        ax.xaxis.set_minor_locator(MinuteLocator(interval=2))

    #ax.axvline(tTC[tReqInd], color='white', linestyle='--',label='Req. Time')
    ax.axvline(tctime['tstartPrecip'], color='red', linestyle='--', label='Precip. Start')
    ax.axvline(tctime['tendPrecip'], color='red', linestyle='--',label='Precip. End')

def doPlot(t,iono, pp, infile,cmap,tctime,sfmt,verbose):
    if t.size<2:  # need at least 2 times for pcolormesh
        return
        
    alt = iono.alt_km
#%% ISR plasma parameters
    for p,cn in zip(ISRPARAM,(LogNorm(),None,None,None)):
        doplot1d(pp.sel(isrparam=p).values,alt,p,sfmt,infile,tctime)
        fg =  figure(); ax = fg.gca()
        pcm = ax.pcolormesh(alt,t, pp.sel(isrparam=p).values, cmap = cmap, norm=cn)
        tplot(t,tctime,fg,ax,pcm,sfmt,p,infile)
#%% ionosphere state parameters
    if verbose>0:
        for ind in ('n1','n2','n3','n4','n5','n6'):
            fg = figure(); ax=fg.gca()
            pcm = ax.pcolormesh(t,alt,iono[ind].values, cmap= cmap,norm=LogNorm(),
                                vmin=0.1,vmax=1e12)
            tplot(t,tctime,fg,ax,pcm,sfmt,str(ind),infile)

def tplot(t,tctime,fg,ax,pcm,sfmt,ttxt,infile):
    ax.autoscale(True,tight=True)
    ax.set_xlabel('time [UTC]')
    ax.set_ylabel('altitude [km]')
    ax.set_title(ttxt + '\n ' + infile)
    fg.colorbar(pcm,format=sfmt)
    timelbl(t,ax,tctime)
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax.tick_params(axis='both', which='both', direction='out', labelsize=12)

def doplot1d(y,z,name,sfmt,infile,tctime):
    if y.ndim==2: # all times, so pick last time
        y = y[-1,:]

    ax = figure().gca()
    ax.plot(y,z.values)
    ax.set_xlabel(name)
    ax.set_ylabel('altitude')
    ax.set_title(name+'\n'+infile)
    ax.grid(True)
    #ax.yaxis.set_major_formatter(sfmt)
    #timelbl(t,ax,tctime)
    #ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    #ax.autoscale(True)
