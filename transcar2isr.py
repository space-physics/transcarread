#!/usr/bin/env python
"""
Reads output of Transcar sim, yielding Incoherent Scatter Radar plasma parameters.

examples:
./test_readtra.py tests/data/beam52/dir.output/transcar_output

"""
from pathlib import Path
from matplotlib.pyplot import show
# ,LogFormatter,LogFormatterMathtext #for 1e4 -> 1 x 10^4, applied DIRECTLY in format=
from matplotlib.ticker import ScalarFormatter
# from matplotlib.ticker import MultipleLocator
from argparse import ArgumentParser
import transcarread.plots as plots
import transcarread as tr
#
sfmt = ScalarFormatter()
#    sfmt = LogFormatter()
#    sfmt.set_scientific(True)
#    sfmt.set_useOffset(False)
#    sfmt.set_powerlimits((-2, 2))


def compute(fn, tReq, verbose):
    # %% get sim parameters
    datfn = Path(fn).parents[1]/'dir.input/DATCAR'
    tctime = tr.readTranscarInput(datfn)
# %% load transcar output
    iono = tr.read_tra(fn, tReq)
# %% do plot
    plots.plotisr(iono, fn, 'cubehelix', tctime, sfmt, verbose)

    return iono, tctime


def main():
    p = ArgumentParser(description='reads dir.output/transcar_output')
    p.add_argument('tofn', help='dir.output/transcar_output file to use')
    p.add_argument('--tReq', help='time to extract data at')
    p.add_argument('-v', '--verbose', help='more plots',
                   action='count', default=0)
    p = p.parse_args()

    iono, tctime = compute(p.tofn, p.tReq, p.verbose)

    show()


if __name__ == '__main__':
    main()
