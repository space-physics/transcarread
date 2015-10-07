#!/usr/bin/env python3
from __future__ import division,absolute_import
import logging
from numpy import asarray, s_, empty
from os.path import expanduser,join
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from pytz import UTC
from pandas import DataFrame, Panel
from matplotlib.pyplot import figure
"""
Michael Hirsch 2014
Parses the ASCII dir.output/emissions.dat in milliseconds
based on transconvec_13

outputs:
excrate: Panel of reaction x altitude x time

variables:
------------
Nalt: number of altitudes in simulation (not necessarily uniform spacing!)
nen:
dipangle,cdip: dip angle of B-field (degrees)
timeop,ctime: time of simulation step (UTC)
zop: altitudes [km]
Nprecip: At the end of each time step, there are this many elements of precipitation data to read
NprecipCol: 2, this accounts for e and fluxdown (each taking one column)
NdataCol: number of data elements per altitude + 1
NumData: number of data elements to read at this time step
"""
NumPerRow = 5 #FIXME I think this is true (!)
NdataCol = 11 #FIXME assuming this is always true (seems likely)
NprecipCol = 2


def ExcitationRates(datadir,infile='emissions.dat'):
    excrate, dipangle, precip, t = readexcrates(join(datadir,'dir.output'), infile)
    # breakup slightly to meet needs of simpler external programs
    #z = excite.major_axis.values
    return excrate, t, dipangle

def initparams(datadir,infile):
    kinfn =   join(expanduser(datadir), infile)

    try:
        with open(kinfn, 'r') as fid: #going to rewind after this priming read
            line = fid.readline()
    except IOError as e:
        logging.error('could not read/find file {}  due to {}'.format(kinfn,e))
        return (None,)*8

    ctime,dip,nalt,nen = getHeader(line)

    Nprecip = NprecipCol * nen # how many precip elements to read at this time step
    ndat = NdataCol * nalt #how many elements to read at this time step
    # how many rows of data (less header) to read in a batch
    ndatrow = (ndat + Nprecip)//NumPerRow  + 1

    logging.debug('{} {} Nalt: {} nen: {} dipangle[deg]: {:.2f}'.format(kinfn,ctime,nalt,nen,dip))

    return kinfn,nalt,nen,dip,ctime,ndatrow,ndat,Nprecip

def readexcrates(datadir,infile):
    kinfn,nalt,nen,dipangle,ctime,ndatrow,ndat,Nprecip = initparams(datadir,infile)
    if kinfn is None:
        return (None,)*4
    #using read_csv was vastly slower!

    with open(kinfn,'r') as f:
        dstream = asarray(f.read().split()).astype(float)
    #print(time()-tic)
    nhead = NumPerRow
    size_record = ndat + Nprecip + nhead
    n_t = dstream.size//size_record

    t = empty(n_t,dtype=dt)
    excf = {}; pf = {}
    for i in range(n_t):
        cind = s_[i*size_record:(i+1)*size_record]
        crec = dstream[cind]

        #h = crec[:nhead] #unused
        d = crec[nhead:-Nprecip].reshape((nalt,NdataCol),order='C')
        # blank nan are between data and precip
        p = crec[-Nprecip:].reshape((nen,NprecipCol),order='C')

        t[i] = parseheadtime(crec[:2])
        excf[t[i].strftime('%Y-%m-%dT%H:%M:%S%Z')] = DataFrame(d[:,1:],
                                   index=d[:,0],
                                   columns=('no1d','no1s','noii2p','nn2a3',
                                             'po3p3p','po3p5p',
                                             'p1ng','pmein','p2pg','p1pg'))

        pf[t[i].strftime('%Y-%m-%dT%H:%M:%S%Z')] = DataFrame(p,
                                                      columns=('e','fluxdown'))

    excrate = Panel(excf).transpose(2,1,0) #turn dict of DataFrames into Panel, index is datetime
    precip = Panel(pf) #dict to Panel, index is datetime
    return excrate, dipangle, precip, t

def getHeader(line):
    """
    head[0]: Year, day of year YYYYDDD
    head[1]: second of day from midnight UTC
    head[2]: 90 - head[2] = B-field dipangle [deg]
    head[3]: Nalt
    head[4]: nen
    """
    head = line.split(None) #None: multiple whitespace as one
    assert len(head) == 5
    timeop = parseheadtime(head) #dt.strptime(head[0],'%Y%j').replace(tzinfo=UTC) + relativedelta(seconds=float(head[1]))
    dipangle = 90. - float(head[2])
    nalt = int(head[3])
    nen = int(head[4])

    return timeop, dipangle, nalt, nen

def parseheadtime(h):
    return dt.strptime(str(int(h[0])),'%Y%j').replace(tzinfo=UTC) + relativedelta(seconds=float(h[1]))

#%% plotting
def plotExcrates(spec,tReq=None):
    if isinstance(spec,Panel) and isinstance(tReq,dt):
        spec = spec.loc[:,:,tReq]
    elif isinstance(spec,Panel):
        spec = spec.iloc[:,:,-1]
    elif isinstance(spec,DataFrame):
        pass
    else:
        return

    ax = figure().gca()
    ax.plot(spec.values,spec.index)
    ax.set_xscale('log')
    ax.set_xlim(left=1e-4)
    ax.set_xlabel('Excitation')
    ax.set_ylabel('altitude [km]')
    ax.set_title('excitation rates')
    ax.legend(spec.columns)
    ax.grid(True)
