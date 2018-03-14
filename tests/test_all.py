#!/usr/bin/env python
"""
examples:
./test_readtra.py tests/data/beam52/dir.output/transcar_output

"""
from pathlib import Path
from datetime import datetime
from pytz import UTC
from numpy.testing import assert_allclose,run_module_suite
#
import transcarread as tr
#
tdir  = Path(__file__).parent
infn = tdir / 'data/beam52/dir.input/90kmmaxpt123.dat'


def test_readtra():
#%% get sim parameters
    ifn   = tdir / 'data/DATCAR'
    tcofn = tdir / 'data/beam52/dir.output/transcar_output'
    tReq = '2013-03-31T09:00:21'
    H = tr.readTranscarInput(ifn)
#%% load transcar output
    iono,chi, pp = tr.read_tra(tcofn, tReq)
#%% check
    assert_allclose(H['latgeo_ini'], 65.12)
    assert_allclose(iono.loc[:,'n1'][30], 2.0969721e+11)
    assert_allclose(chi,110.40122986)
    assert_allclose(pp.loc[:,'Ti'][53], 1285.927001953125)


def test_readtranscar():
    e0 = 52.
    tReq = '2013-03-31T09:00:21'
    sim = tr.SimpleSim('bg3', tdir/f'data/beam{e0}/dir.output')
    excrates, tUsed, tReqInd = tr.calcVERtc('dir.output/emissions.dat',tdir/'data', e0,tReq,sim)
#%%
    assert_allclose(excrates.loc[:,'no1d'][0,53],15638.620000000001)
    assert tUsed == datetime(2013, 3, 31, 9, 0, 42, tzinfo=UTC)
    assert_allclose(tReqInd,0)


def test_readmsis():
    msisi,hdi,ppi = tr.readmsis(infn)


if __name__=='__main__':
    run_module_suite()
