#!/usr/bin/env python3
"""
examples:
./test_readtra.py ~/code/transcar/out/ifort2/beam3915.4/dir.output/transcar_output

"""
from transcarread import Path
from datetime import datetime
from pytz import UTC
from numpy.testing import assert_allclose,run_module_suite
#
from transcarread.read_tra import read_tra
from transcarread.parseTranscar import readTranscarInput
from transcarread.readTranscar import calcVERtc,SimpleSim

tdir  = Path(__file__).parent

def test_readtra():
#%% get sim parameters
    ifn   = tdir / 'data/DATCAR'
    tcofn = tdir / 'data/beam52.726/dir.output/transcar_output'
    tReq = datetime(2013,3,31,9,0,21,tzinfo=UTC)
    H = readTranscarInput(ifn)
#%% load transcar output
    iono,chi, pp = read_tra(tcofn,tReq)
#%% check
    assert_allclose(H['latgeo_ini'],65.12)
    assert_allclose(iono['n1'].iloc[30],2.0969721e+11)
    assert_allclose(chi,110.40122986)
    assert_allclose(pp['Ti'].iloc[53],1285.927001953125)

def test_readtranscar():
    tReq = datetime(2013,3,31,9,0,21,tzinfo=UTC)
    sim = SimpleSim('bg3',tdir/'data/beam52.726/dir.output')
    excrates, tUsed, tReqInd = calcVERtc('emissions.dat',tdir/'data',52.726,tReq,sim)
#%%
    assert_allclose(excrates['no1d'].iloc[53,0],15638.620000000001)
    assert tUsed==datetime(2013, 3, 31, 9, 0, 42, tzinfo=UTC)
    assert_allclose(tReqInd,0)

if __name__=='__main__':
    run_module_suite()
