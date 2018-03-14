#!/usr/bin/env python
""" test readexcrates.py
"""
from pathlib import Path
from transcarread import ExcitationRates
from transcarread.plots import plotExcrates
import seaborn as sns
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

    if path.stem.startswith('beam'):
        dlist = [path]
    else:
        dlist = [d for d in path.iterdir() if d.is_dir()]

    for d in dlist:
        spec = ExcitationRates(d/p.emisfn)
        spec.name = d.name[4:]
        plotExcrates(spec)

    show()
