#!/usr/bin/env python
""" test readexcrates.py
"""
from pathlib import Path
import sys
from transcarread import ExcitationRates
from transcarread.plots import plotExcrates
import seaborn as sns
#
sys.tracebacklimit=2 # 1 gave IndexError needlessly
#%% command line
if __name__=='__main__':
    from matplotlib.pyplot import show
    from argparse import ArgumentParser
    p = ArgumentParser(description='Read Transcar excitation rates')
    p.add_argument('--emisfn',help='emissions.dat filename',default='dir.output/emissions.dat')
    p.add_argument('path',help='path where dir.output/emissions.dat is')
    p.add_argument('--profile',help='profile performance',action='store_true')
    p = p.parse_args()

    path = Path(p.path).expanduser()

    if p.profile:
        import cProfile,pstats
        proffn = 'excstats.pstats'
        cProfile.run('ExcitationRates(p.path,p.emisfn)',proffn)
        pstats.Stats(proffn).sort_stats('time','cumulative').print_stats(50)
    else:
        if path.stem.startswith('beam'):
            dlist = [path]
        else:
            dlist = [d for d in path.iterdir() if d.is_dir()]

        for d in dlist:
            spec,timeop,dipangle= ExcitationRates(d/p.emisfn)
            spec.name = d.name[4:]
            plotExcrates(spec)

        show()
