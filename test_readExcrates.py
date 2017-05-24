#!/usr/bin/env python
""" test readexcrates.py
"""
from transcarread import ExcitationRates
from transcarread.plots import plotExcrates
import seaborn as sns

#%% command line
if __name__=='__main__':
    from matplotlib.pyplot import show
    from argparse import ArgumentParser
    p = ArgumentParser(description='Read Transcar excitation rates')
    p.add_argument('--emisfn',help='emissions.dat filename',default='emissions.dat')
    p.add_argument('path',help='path where dir.output/emissions.dat is')
    p.add_argument('--profile',help='profile performance',action='store_true')
    p = p.parse_args()

    if p.profile:
        import cProfile,pstats
        proffn = 'excstats.pstats'
        cProfile.run('ExcitationRates(p.path,p.emisfn)',proffn)
        pstats.Stats(proffn).sort_stats('time','cumulative').print_stats(50)
    else:
        spec,timeop,dipangle= ExcitationRates(p.path,p.emisfn)
        plotExcrates(spec)
        show()
