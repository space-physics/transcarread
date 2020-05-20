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


def compute(path: Path, tReq: datetime, plot_params: list):
    path = Path(path).expanduser().resolve()
    # %% get sim parameters
    datfn = path / "dir.input/DATCAR"
    tctime = tr.readTranscarInput(datfn)
    # %% load transcar output
    iono = tr.read_tra(path, tReq)

    return iono, tctime


def main():
    p = ArgumentParser(description="reads dir.output/transcar_output")
    p.add_argument("ref", help="old reference path above dir.output/")
    p.add_argument("new", help="path above new dir.output/")
    p.add_argument("--tReq", help="time to extract data at")
    p.add_argument("-p", "--params", help="only plot these params", choices=["ne", "vi", "Ti", "Te"], nargs="+")
    p = p.parse_args()

    dat1, t1 = compute(p.ref, p.tReq, p.params)
    dat2, t2 = compute(p.new, p.tReq, p.params)

    diff = dat1-dat2
    # %% do plot
    plots.plot_isr(diff, p.new, t2, p.params)

    show()


if __name__ == "__main__":
    main()
