#!/usr/bin/env python
"""
read/plot precipitation flux

one beam specific directory

    python precip_flux.py tests/data/beam52

many beams under this directory

    python precip_flux.py tests/data/
"""
from pathlib import Path
from matplotlib.pyplot import show
from argparse import ArgumentParser

from transcarread import read_precinput
from transcarread.plots import plot_precinput


def main():
    p = ArgumentParser(description="Read Transcar precipitation differential number flux")
    p.add_argument("--fn", help="precinput filename", default="dir.input/precinput.asc")
    p.add_argument("path", help="dir.input/precinput is under")
    p = p.parse_args()

    path = Path(p.path).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(path)

    phi = read_precinput(path / p.fn)

    plot_precinput(phi, path.name)

    show()


if __name__ == "__main__":
    main()
