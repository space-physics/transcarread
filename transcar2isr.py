#!/usr/bin/env python
"""
Reads output of Transcar sim, yielding Incoherent Scatter Radar plasma parameters.

examples:
./test_readtra.py ~/data/beam3915.4/dir.output/transcar_output

"""
from dateutil.parser import parse
from pathlib import Path
from matplotlib.pyplot import show
from matplotlib.ticker import ScalarFormatter#,LogFormatter,LogFormatterMathtext #for 1e4 -> 1 x 10^4, applied DIRECTLY in format=
#from matplotlib.ticker import MultipleLocator
#
from transcarread.plots import plotisr
from transcarread import readTranscarInput,read_tra
#
sfmt=ScalarFormatter()
#    sfmt = LogFormatter()
#    sfmt.set_scientific(True)
#    sfmt.set_useOffset(False)
#    sfmt.set_powerlimits((-2, 2))

def main(fn,tReq,verbose):
#%% get sim parameters
    datfn = Path(fn).parents[1]/'dir.input/DATCAR'
    tctime = readTranscarInput(datfn)

    if isinstance(tReq,str):
        tReq = parse(tReq)

#%% load transcar output
    iono,chi, pp = read_tra(fn,tReq)
#%% do plot
    t = pp.time
    plotisr(t,iono,pp, fn, 'cubehelix',tctime,sfmt,verbose)

    #doplot1d(t,chi,'$\chi$',sfmt,fn, tctime)

    return iono,chi,pp,t,tctime

if __name__=='__main__':
    from argparse import ArgumentParser

    p = ArgumentParser(description='reads dir.output/transcar_output')
    p.add_argument('tofn',help='dir.output/transcar_output file to use')
    p.add_argument('--tReq',help='time to extract data at')
    p.add_argument('--profile',help='profile performance',action='store_true')
    p.add_argument('--noplot',help='disable plotting',action="store_true")
    p.add_argument('-v','--verbose',help='more plots',action='count',default=0)
    p = p.parse_args()

    doplot = not p.noplot

    if p.profile:
        import cProfile
        from pstats import Stats
        profFN = 'read_tra.pstats'
        print('saving profile results to ' + profFN)
        cProfile.run('main(p.tofn)',profFN)
        Stats(profFN).sort_stats('time','cumulative').print_stats(50)
    else:
        iono,chi,pp,t,tctime = main(p.tofn,p.tReq,p.verbose)
        show()
