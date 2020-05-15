#!/usr/bin/env python
"""
read excitation rates and plot

    # one beam specific directory
    python excitation_rates.py tests/data/beam52

    # many beams under this directory
    python excitation_rates.py tests/data/
"""
from pathlib import Path
from matplotlib.pyplot import show
from argparse import ArgumentParser
from transcarread import ExcitationRates
from transcarread.plots import plotExcrates


def main():
    p = ArgumentParser(description="Read Transcar excitation rates")
    p.add_argument("--emisfn", help="emissions.dat filename", default="dir.output/emissions.dat")
    p.add_argument("path", help="path where dir.output/emissions.dat is")
    p = p.parse_args()

    path = Path(p.path).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(path)

    if path.stem.startswith("beam"):  # specific beam
        dirs = [path]
    else:  # overall simulation
        dirs = sorted(d for d in path.iterdir() if (d / p.emisfn).is_file())

    if not dirs:
        raise FileNotFoundError(f"did not find beams in {path}")
    for d in dirs:
        rates = ExcitationRates(d / p.emisfn)
        rates.name = d.name[4:]
        plotExcrates(rates)

    show()


if __name__ == "__main__":
    main()
