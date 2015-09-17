from __future__ import division,absolute_import
from pandas import DataFrame

def compplasmaparam(iono,approx):

    pp = DataFrame(index=iono.index,
                   columns=('ne','vi','Ti','Te'))

    nm = iono[['n4','n5','n6']].sum(axis=1)

    pp['ne'] = comp_ne(iono)
    pp['vi'] = comp_vi(iono,nm,pp)
    pp['Ti'] = comp_Ti(iono,nm,pp)
    pp['Te'] = comp_Te(iono,approx)
    return pp

def comp_ne(d):
    return (d[['n1','n2','n3','n4','n5','n6','n7']].sum(axis=1))

def comp_vi(d,nm,pp):
    return (d[['n1','v1']].prod(axis=1) +
            d[['n2','v2']].prod(axis=1) +
            d[['n3','v3']].prod(axis=1) +
            nm * d['vm']) / pp['ne']

def comp_Ti(d,nm,pp):
    """transconvec_13.op.f
    read_fluidmod.m, data_tra.m
    """

    Tipar= (d[['n1','t1p']].prod(axis=1) +
            d[['n2','t2p']].prod(axis=1) +
            d[['n3','t3p']].prod(axis=1) +
            nm * d['tmp']) / pp['ne']

    Tiperp=(d[['n1','t1t']].prod(axis=1) +
            d[['n2','t2t']].prod(axis=1) +
            d[['n3','t3t']].prod(axis=1) +
            nm * d['tmt']) / pp['ne']
    #return (n1*t1 + n2*t2 + n3*t3 +nm*tm)/(n1 +n2 +n3 +nm)
    return (1/3)*Tipar + (2/3)*Tiperp

def comp_Te(d,approx):
    if int(approx)==13:
        return (d['tep'] + 2*d['tet']).astype(float) / 3
    else:
        return d['tep'].astype(float)