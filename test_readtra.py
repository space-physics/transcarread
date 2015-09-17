#!/usr/bin/env python3
"""
examples:
./test_readtra.py ~/code/histfeas/test/data/beam3915.4

"""
from os.path import split, join
from matplotlib.pyplot import show
from matplotlib.ticker import ScalarFormatter#,LogFormatter,LogFormatterMathtext #for 1e4 -> 1 x 10^4, applied DIRECTLY in format=
#from matplotlib.ticker import MultipleLocator
#
from transcarread.read_tra import doPlot,doPlot1d
from transcarread.parseTranscar import readTranscarInput

def main(fn):
    datfn = join(split(split(fn)[0])[0],'dir.input/DATCAR')
    tctime = readTranscarInput(datfn)

    #sfmt = LogFormatter()
    sfmt=ScalarFormatter()
    #sfmt.set_scientific(True)
   # sfmt.set_useOffset(False)
   # sfmt.set_powerlimits((-2, 2))

#%% do plot
    t = pp.minor_axis.to_datetime().to_pydatetime()
    doPlot(t,iono,pp, fn, 'jet',tctime,sfmt)

    doPlot1d(t,chi,sfmt,fn, tctime)

if __name__=='__main__':
    from argparse import ArgumentParser

    p = ArgumentParser(description='reads dir.output/transcar_output')
    p.add_argument('tofn',help='dir.output/transcar_output file to use')
    p.add_argument('--profile',help='profile performance',action='store_true')
    p.add_argument('--noplot',help='disable plotting',action="store_true")
    p = p.parse_args()
    doplot = not p.noplot
    #tcoutput = '~/transcar/AT1/beam11335./dir.output/transcar_output'
    doplot = not p.noplot

    if p.profile:
        import cProfile
        from pstats import Stats
        profFN = 'read_tra.pstats'
        print('saving profile results to ' + profFN)
        cProfile.run('main(p.tofn)',profFN)
        Stats(profFN).sort_stats('time','cumulative').print_stats(50)
    else:
        iono,chi,pp = main(p.tofn)
        show()
