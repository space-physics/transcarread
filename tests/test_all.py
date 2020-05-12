#!/usr/bin/env python
from pathlib import Path
import numpy as np
import pytest
from datetime import datetime
from pytest import approx

import transcarread as tr

#
tdir = Path(__file__).parent
infn = tdir / "data/beam52.7/dir.input/90kmmaxpt123.dat"


def test_readtra():
    # %% get sim parameters
    ifn = infn.parents[1] / "dir.input/DATCAR"
    tcofn = tdir / "data/beam52.7"
    tReq = "2013-03-31T09:00:21"
    H = tr.readTranscarInput(ifn)
    # %% load transcar output
    iono = tr.read_tra(tcofn, tReq)
    # %% check
    assert H["latgeo_ini"] == approx(65.12)
    assert iono["iono"].loc[..., "n1"][30] == approx(2.0969721e11)
    assert iono.attrs["chi"] == approx(110.40122986)
    assert iono["pp"].loc[..., "Ti"][53] == approx(1285.927001953125)


def test_readtranscar():
    e0 = 52.7
    tReq = datetime(2013, 3, 31, 9, 0, 21)
    rates = tr.calcVERtc(tdir / "data/beam52.7", tReq, tdir / f"data/beam{e0}/dir.input/DATCAR")
    # %%
    assert rates.loc[:, "no1d"][53] == approx(15638.62)
    assert rates.time.values == np.datetime64("2013-03-31T09:00:42")


def test_readmsis():
    msis = tr.readmsis(infn)
    assert msis["msis"].loc[..., "no1d"][53] == approx(116101103616.0)


if __name__ == "__main__":
    pytest.main([__file__])
