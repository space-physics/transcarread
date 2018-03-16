#!/usr/bin/env python
"""
examples:
./test_readtra.py tests/data/beam52/dir.output/transcar_output

"""
from pathlib import Path
import numpy as np
from numpy.testing import assert_allclose,run_module_suite
#
import transcarread as tr
#
tdir  = Path(__file__).parent
infn = tdir / 'data/beam52/dir.input/90kmmaxpt123.dat'


def test_readtra():
#%% get sim parameters
    ifn   = infn.parents[1] / 'dir.input/DATCAR'
    tcofn = tdir / 'data/beam52/dir.output/transcar_output'
    tReq = '2013-03-31T09:00:21'
    H = tr.readTranscarInput(ifn)
#%% load transcar output
    iono = tr.read_tra(tcofn, tReq)
#%% check
    assert_allclose(H['latgeo_ini'], 65.12)
    assert_allclose(iono['iono'].loc[...,'n1'][30], 2.0969721e+11)
    assert_allclose(iono.attrs['chi'],110.40122986)
    assert_allclose(iono['pp'].loc[...,'Ti'][53], 1285.927001953125)


def test_readtranscar():
    e0 = 52.
    tReq = '2013-03-31T09:00:21'
    sim = tr.SimpleSim('bg3', tdir/f'data/beam{e0}/dir.output')
    rates = tr.calcVERtc('dir.output/emissions.dat',tdir/'data', e0,tReq,sim)
#%%
    assert_allclose(rates.loc[...,'no1d'][53], 15638.62)
    assert rates.time.values == np.datetime64('2013-03-31T09:00:42')


def test_readmsis():
    msis = tr.readmsis(infn)
    assert_allclose(msis['msis'].loc[...,'no1d'][53], 116101103616.0)

if __name__=='__main__':
    run_module_suite()
