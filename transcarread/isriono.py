from numpy import empty
from xarray import DataArray

def compplasmaparam(iono,approx):
    assert isinstance(iono,DataArray)

    pp = DataArray(empty((iono.shape[0],4)),
                   coords=[('alt_km',iono.alt_km),
                           ('isrparam',['ne','vi','Ti','Te'])]
                   )

    nm = iono[['n4','n5','n6']].sum(axis=1)

    pp.loc[:,'ne'] = comp_ne(iono)
    pp.loc[:'vi'] = comp_vi(iono,nm,pp)
    pp.loc[:,'Ti'] = comp_Ti(iono,nm,pp)
    pp.loc[:,'Te'] = comp_Te(iono,approx)
    return pp

def comp_ne(d):
    return (d.loc[:,['n1','n2','n3','n4','n5','n6','n7']].sum('isrparam'))

def comp_vi(d,nm,pp):
    return (d.loc[:,['n1','v1']].prod('isrparam') +
            d.loc[:,['n2','v2']].prod('isrparam') +
            d.loc[:,['n3','v3']].prod('isrparam') +
            nm * d.loc[:,'vm']) / pp.loc[:,'ne']

def comp_Ti(d,nm,pp):
    """transconvec_13.op.f
    read_fluidmod.m, data_tra.m
    """

    Tipar= (d.loc[:,['n1','t1p']].prod('isrparam') +
            d.loc[:,['n2','t2p']].prod('isrparam') +
            d.loc[:,['n3','t3p']].prod('isrparam') +
            nm * d.loc[:,'tmp']) / pp.loc[:,'ne']

    Tiperp=(d.loc[:,['n1','t1t']].prod('isrparam') +
            d.loc[:,['n2','t2t']].prod('isrparam') +
            d.loc[:,['n3','t3t']].prod('isrparam') +
            nm * d.loc[:,'tmt']) / pp.loc[:,'ne']
    #return (n1*t1 + n2*t2 + n3*t3 +nm*tm)/(n1 +n2 +n3 +nm)
    return (1/3)*Tipar + (2/3)*Tiperp

def comp_Te(d,approx):
    if int(approx)==13:
        return (d.loc[:,'tep'] + 2*d.loc[:,'tet']).astype(float) / 3
    else:
        return d.loc[:,'tep'].astype(float)