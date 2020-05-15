#!/usr/bin/env python
"""
Reads output of Transcar sim, yielding Incoherent Scatter Radar plasma parameters.

    python transcar2isr.py tests/data/beam52

"""
from pathlib import Path
from matplotlib.pyplot import show
from argparse import ArgumentParser
from datetime import datetime

#
import transcarread.plots as plots
import transcarread as tr


def compute(path: Path, tReq: datetime, verbose: bool):
    path = Path(path).expanduser().resolve()
    # %% get sim parameters
    datfn = path / "dir.input/DATCAR"
    tctime = tr.readTranscarInput(datfn)
    # %% load transcar output
    iono = tr.read_tra(path, tReq)
    # %% do plot
    plots.plot_isr(iono, path, tctime, verbose)

    return iono, tctime


def main():
    p = ArgumentParser(description="reads dir.output/transcar_output")
    p.add_argument("path", help="path containing dir.output/transcar_output file")
    p.add_argument("--tReq", help="time to extract data at")
    p.add_argument("-v", "--verbose", help="more plots", action="store_true")
    p = p.parse_args()

    compute(p.path, p.tReq, p.verbose)

    show()


if __name__ == "__main__":
    main()
