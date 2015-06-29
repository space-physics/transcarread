#!/usr/bin/env python3
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from pytz import UTC
from os.path import expanduser
'''
The transcar input file is indexed by line number --this is what the Fortran
  #  code of transcar does, and it's what we do here as well.
'''
def readTranscarInput(infn):
    infn = expanduser(infn)
    hd = {}
    try:
      with open(infn,'r') as f:
        hd['kiappel'] =           int(f.readline().split(None)[0])
        hd['precfile'] =              f.readline().split(None)[0]
        hd['dtsim'] =           float(f.readline().split(None)[0]) #"dto"
        hd['dtfluid'] =         float(f.readline().split(None)[0]) #"sortie"
        hd['iyd_ini'] =         int(f.readline().split(None)[0])
        hd['dayofsim'] =  dt.strptime(str(hd['iyd_ini']),'%Y%j').replace(tzinfo=UTC)
        hd['simstartUTCsec'] =  float(f.readline().split(None)[0]) #"tempsini"
        hd['simlengthsec'] =    float(f.readline().split(None)[0]) #"tempslim"
        hd['jpreci'] =            int(f.readline().split(None)[0])
        # transconvec calls the next two latgeo_ini, longeo_ini
        hd['latgeo_ini'], hd['longeo_ini'] = [float(a) for a in f.readline().split(None)[0].split(',')]
        hd['tempsconv_1'] = float(f.readline().split(None)[0]) #from transconvec, time before precip
        hd['tempsconv'] =float(f.readline().split(None)[0]) #from transconvec, time after precip
        hd['step'] =    float(f.readline().split(None)[0])
        hd['dtkinetic'] =       float(f.readline().split(None)[0]) #transconvec calls this "postinto"
        hd['vparaB'] =  float(f.readline().split(None)[0])
        hd['f107ind'] =         float(f.readline().split(None)[0])
        hd['f107avg'] =         float(f.readline().split(None)[0])
        hd['apind'] =           float(f.readline().split(None)[0])
        hd['convecEfieldmVm'] = float(f.readline().split(None)[0])
        hd['cofo'] =            float(f.readline().split(None)[0])
        hd['cofn2'] =           float(f.readline().split(None)[0])
        hd['cofo2'] =           float(f.readline().split(None)[0])
        hd['cofn'] =            float(f.readline().split(None)[0])
        hd['cofh'] =            float(f.readline().split(None)[0])
        hd['etopflux'] =        float(f.readline().split(None)[0])
        hd['precinfn'] =              f.readline().split(None)[0]
        hd['precint'] =           int(f.readline().split(None)[0])
        hd['precext'] =           int(f.readline().split(None)[0])
        hd['precipstartsec'] =  float(f.readline().split(None)[0])
        hd['precipendsec'] =    float(f.readline().split(None)[0])

        # derived parameters not in datcar file
        hd['tstartSim'] =    hd['dayofsim'] + relativedelta(seconds=hd['simstartUTCsec'])
        hd['tendSim'] =      hd['dayofsim'] + relativedelta(seconds=hd['simlengthsec']) #TODO verify this isn't added to start
        hd['tstartPrecip'] = hd['dayofsim'] + relativedelta(seconds=hd['precipstartsec'])
        hd['tendPrecip'] =   hd['dayofsim'] + relativedelta(seconds=hd['precipendsec'])
    except IOError as e: #python 2.7 doesn't have FileNotFoundError
        print(e)
        return None

    return hd

if __name__ == '__main__':
    from pprint import pprint
    from argparse import ArgumentParser
    p = ArgumentParser(description='reads transcar dir.input/DATCAR file')
    p.add_argument('infn',help='path to dir.input/DATCAR',type=str,nargs='?',default='~/code/transcar/dir.transcar.server/dir.input/DATCAR')
    a = p.parse_args()

    ptime = readTranscarInput(a.infn)
    pprint(ptime)
