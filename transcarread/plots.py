from datetime import datetime
from pathlib import Path
import xarray
import logging
from matplotlib.pyplot import figure
from matplotlib.dates import DateFormatter,MinuteLocator, SecondLocator
from matplotlib.colors import LogNorm
#
from . import ISRPARAM


def timelbl(time,ax,tctime):
    """improve time axis labeling"""
    if time.size<200:
        ax.xaxis.set_minor_locator(SecondLocator(interval=10))
        ax.xaxis.set_minor_locator(SecondLocator(interval=2))
    elif time.size<500:
        ax.xaxis.set_minor_locator(MinuteLocator(interval=10))
        ax.xaxis.set_minor_locator(MinuteLocator(interval=2))

    #ax.axvline(tTC[tReqInd], color='white', linestyle='--',label='Req. Time')
    ax.axvline(tctime['tstartPrecip'], color='red', linestyle='--', label='Precip. Start')
    ax.axvline(tctime['tendPrecip'], color='red', linestyle='--',label='Precip. End')


def plotisr(iono:xarray.Dataset, infile:Path, tctime:dict,
            cmap:str=None, sfmt=None, verbose:bool=False):
    """Plot Transcar ISR parameters"""
    t = iono.time
    if t.size<2:  # need at least 2 times for pcolormesh
        logging.error('unable to plot with less than 2 time steps')
        return

    alt = iono.alt_km
#%% ISR plasma parameters
    for p,cn in zip(ISRPARAM,(LogNorm(),None,None,None)):
        _plot1d(iono['pp'].loc[:,p], alt, p, sfmt, infile, tctime)
        fg =  figure(); ax = fg.gca()
        pcm = ax.pcolormesh(alt, t, iono['pp'].loc[:,p], cmap = cmap, norm=cn)
        _tplot(t,tctime,fg,ax,pcm,sfmt,p,infile)
#%% ionosphere state parameters
    if verbose>0:
        for ind in ('n1','n2','n3','n4','n5','n6'):
            fg = figure(); ax=fg.gca()
            pcm = ax.pcolormesh(t,alt,iono[ind].values, cmap= cmap,norm=LogNorm(),
                                vmin=0.1,vmax=1e12)
            _tplot(t,tctime,fg,ax,pcm,sfmt,str(ind),infile)


def _tplot(t,tctime,fg,ax,pcm,sfmt,ttxt,infile):
    ax.autoscale(True,tight=True)
    ax.set_xlabel('time [UTC]')
    ax.set_ylabel('altitude [km]')
    ax.set_title(ttxt + '\n ' + infile)
    fg.colorbar(pcm,format=sfmt)
    timelbl(t,ax,tctime)
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax.tick_params(axis='both', which='both', direction='out', labelsize=12)


def _plot1d(y,z,name,sfmt,infile,tctime):
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

def plotionoinit(msis:xarray.DataArray):
    """plot Transcar ionosphere initial condition data"""

    figure(1).clf()
    ax= figure(1).gca()
    for i in [f'n{j}' for j in range(1,7)]:
        ax.plot(msis.loc[:,i], msis.alt_km, label=i)

    ax.set_xscale('log')
    ax.legend(loc='best')
#    #msis.plot(y='alt',x='n4',title=ifn,logx=True) # why doesn't this plot correctly?
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('n [m$^{-3}$]')
    ax.set_title(f'{msis.attrs["filename"]} \n Density components')
# %% velocities
    figure(2).clf()
    ax= figure(2).gca()
    for s in ('v1','v2','v3','ve','vm'):
        ax.plot(msis.loc[:,s], msis.alt_km, label=s)

    ax.set_xlabel('v [m/s]')
    ax.set_ylabel('altitude [km]')
    ax.legend(loc='best')
    ax.grid(True)
    ax.set_title(f'{msis.attrs["filename"]} \n Velocity components')



def plotisrparam(pp:xarray.DataArray, zlim:tuple=None):
    """plot ISR parameter data"""
    fg = figure(figsize=(12,5))
    fg.suptitle(pp.attrs['filename'])

    ax = fg.subplots(nrows=1,ncols=3,sharey=True)
    ax[0].plot(pp.loc[:,'ne'], pp.alt_km)
    ax[0].set_xlabel('$n_e$ [m$^{-3}$]')
    ax[0].set_ylabel('altitude along B-field line [km]')
    ax[0].set_xscale('log')
    ax[0].set_title('Electron Number Density')

    ax[1].plot(pp.loc[:,'vi'], pp.alt_km)
    ax[1].set_xlabel('$v_i$ [m/s]')
    ax[1].set_title('ion velocity')

    ax[2].plot(pp.loc[:,'Ti'], pp.alt_km, label='$T_i$')
    ax[2].plot(pp.loc[:,'Te'], pp.alt_km, label='$T_e$')
    ax[2].set_xlabel('Temperature [K]')
    ax[2].legend(loc='best')
    ax[2].set_title('Temperatures')

    for a in ax:
        a.set_ylim(zlim)
        a.grid(True)

#    #fg.tight_layout() #no, it spaces the subplots wider
    fg.subplots_adjust(wspace=0.075) #brings subplots horizontally closer


def plotExcrates(rates:xarray.DataArray, tReq:datetime=None):
    if rates.ndim==3 and isinstance(tReq,datetime):
        rates = rates.loc[tReq,...]
    elif rates.ndim==3:
        rates = rates[-1,...]
        print('used last time',rates.time)
    elif rates.ndim==2:
        pass
    else:
        return

    ax = figure().gca()
    ax.plot(rates, rates.alt_km)
    ax.set_xscale('log')
    ax.set_xlim(left=1e-4)
    ax.set_xlabel('Excitation')
    ax.set_ylabel('altitude [km]')
    ax.set_title(f'excitation rates: {rates.name} eV')
    ax.legend(rates.reaction.values)
    ax.grid(True)
