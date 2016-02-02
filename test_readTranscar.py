#!/usr/bin/env python3
from transcarread.readTranscar import calcVERtc,SimpleSim
from dateutil.parser import parse
#%% main (sanity test with hard coded values)
if __name__ == '__main__':

    from argparse import ArgumentParser
    p = ArgumentParser(description='analyzes HST data and makes simulations')
    p.add_argument('path',help='root path that beam directories live in')
    p.add_argument('-e','--energy',help='energy of this beam [eV]',default=2300.5,type=float)
    p.add_argument('-t','--treq',help='date/time  YYYY-MM-DDTHH-MM-SS',default='2013-03-31T09:00:30Z')
    p.add_argument('--profile',help='profile performance',action='store_true')
    p.add_argument('--filter',help='optical filter choices: bg3   none',default='bg3')
    p.add_argument('--tcopath',help='set path from which to read transcar output files',default='dir.output')
    p = p.parse_args()



    infile ='emissions.dat'
    sim = SimpleSim(p.filter,p.tcopath)
#%% run sim
    if p.profile:
        import cProfile,pstats
        proffn = 'readTranscar.pstats'
        cProfile.run('calcVERtc(sim, p.verbose)',proffn)
        pstats.Stats(proffn).sort_stats('time','cumulative').print_stats(50)
    else:
        excrates, tUsed, tReqInd = calcVERtc(infile,p.path,p.energy,parse(p.treq),sim)
