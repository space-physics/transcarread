#!/usr/bin/env python
"""
Show auroral output, optionally with simulated optical filter.

python transcar2aurora.py tests/data/
"""
from argparse import ArgumentParser
from dateutil.parser import parse
import transcarread as tr
try:
    from matplotlib.pyplot import figure, show
except ImportError:
    figure = None


def main():
    p = ArgumentParser(description='Makes auroral emissions based on transcar sim')
    p.add_argument('path', help='root path that beam directories live in')
    p.add_argument('-t', '--treq', help='date/time  YYYY-MM-DDTHH-MM-SS',
                   default='2013-03-31T09:00:30Z')
    p.add_argument('--filter', help='optical filter choices: bg3   none', default='bg3')
    p.add_argument('--tcopath', help='set path from which to read transcar output files', default='dir.output')
    p = p.parse_args()

    sim = tr.SimpleSim(p.filter, p.tcopath, transcarutc=p.treq)
# %% run sim
    rates = tr.calcVERtc(p.path, parse(p.treq), sim)
    print(rates)

    if figure is not None:
        ax = figure().gca()
        ax.semilogx(rates[0, :, :], rates.alt_km)
        ax.set_ylabel('altitude [km]')
        ax.set_xlabel('excitation')
        ax.set_title(str(p.path))

        show()


if __name__ == '__main__':
    main()
