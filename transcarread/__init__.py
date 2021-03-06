import logging
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import interp1d
import xarray
from typing import Tuple, Union, List, IO, Any

#
from .ztanh import setupz
from .io import readTranscarInput, readionoheader, parseionoheader

#
nhead = 126  # a priori from transconvec_13
NumPerRow = 5
NdataCol = 11
NprecipCol = 2
d_bytes = 4
# ncol0 = 50 #from transconvec_13.op.f
# from inspection of "good" .dat file, x1F8=d504, 504 gets us up to this point
headbytes = 504

toobig = 300  # beyond which number of altitude cells transcar will crash


ISRPARAM = ["ne", "vi", "Ti", "Te"]
PARAM = [
    "n1",
    "n2",
    "n3",
    "n4",
    "n5",
    "n6",
    "n7",
    "v1",
    "v2",
    "v3",
    "vm",
    "ve",
    "t1p",
    "t1t",
    "t2p",
    "t2t",
    "t3p",
    "t3t",
    "tmp",
    "tmt",
    "tep",
    "tet",
]
KINFN = "dir.output/emissions.dat"


def read_precinput(path: Path) -> np.ndarray:
    """
    read precipitation input

    Parameters
    ----------

    path : pathlib.Path
        fullpath to precinput file

    Returns
    -------

    phi: numpy.ndarray
        vector of differential number flux
    """

    return np.loadtxt(path, delimiter=" ", skiprows=1, max_rows=34)


def read_tra(path: Path, tReq: datetime = None) -> xarray.DataArray:
    """
    reads binary "transcar_output" file
    many more quantities exist in the binary file, these are the ones we use so far.
    requires: Matplotlib >= 1.4

    examples: test_readtra.py

    Parameters
    ----------
    tcofn: path/filename of transcar_output file
    tReq: optional, datetime at which to extract data from file (will still read whole file first)

    variables:
    n_t: number of time steps in file
    n_alt: number of altitudes in simulation
    d_bytes: number of bytes per data element
    size_record: number of data bytes per time step

    Note: header length = 2*ncol
    """
    tcofn = path / "dir.output/transcar_output"

    hd = readionoheader(tcofn, nhead)[0]

    hd["size_head"] = 2 * hd["ncol"]  # +2 by defn of transconvec_13
    hd["size_data_record"] = hd["nx"] * hd["ncol"]  # data without header
    hd["size_record"] = hd["size_head"] + hd["size_data_record"]

    assert hd["size_head"] == nhead
    # %% read data based on header
    iono = loopread(tcofn, hd, tReq)

    return iono


def loopread(tcofn: Path, hd: dict, tReq: datetime = None) -> xarray.DataArray:

    tcoutput = Path(tcofn).expanduser()
    n_t = tcoutput.stat().st_size // hd["size_record"] // d_bytes

    iono: xarray.DataArray = []
    with tcoutput.open("rb") as f:  # reset to beginning
        for _ in range(n_t):
            iono.append(data_tra(f, hd))

    iono = xarray.concat(iono, "time")
    # %% handle time request -- will return Dataframe if tReq, else returns Panel of all times
    if tReq is not None:  # have to qualify this since picktime default gives last time as fallback
        tUsedInd = picktime(iono.time.values, tReq)[0]
        if tUsedInd is not None:  # in case ind is 0
            iono = iono.isel(time=tUsedInd)

    return iono


def data_tra(f: IO[Any], hd: dict) -> xarray.DataArray:
    # %% parse header
    h = np.fromfile(f, np.float32, nhead)
    head = parseionoheader(h)
    # %% read and index data
    data = np.fromfile(f, np.float32, hd["size_data_record"]).reshape((hd["nx"], hd["ncol"]), order="C")

    dextind = tuple(range(1, 7)) + (49,) + tuple(range(7, 13))
    if head["approx"] >= 13:
        dextind += tuple(range(13, 22))
    else:
        dextind += (12, 13, 13, 14, 14, 15, 15, 16, 16)
    # n7=49 if ncol>49 else None

    iono = xarray.DataArray(data[:, dextind], coords=[("alt_km", data[:, 0]), ("isrparam", PARAM)], attrs={"filename": f.name})
    # %% four ISR parameters
    """
    ion velocity from read_fluidmod.m
    data_tra.m does not consider n7 for ne or vi computation,
    BUT read_fluidmod.m does consider n7!
    """
    pp = compplasmaparam(iono, head["approx"])
    # %% output
    iono = xarray.Dataset({"iono": iono, "pp": pp}, coords={"time": head["htime"]}, attrs={"chi": head["chi"]})

    return iono


# %% read iono
def readmsis(ifn: Path, ofn: Path = None, dz=None, newaltmethod: str = None):
    """reads MSIS model output that Transcar uses"""

    nhead = headbytes // d_bytes

    hd, hdraw = readionoheader(ifn, nhead)

    msis, raw = readinitconddat(hd, ifn)  # index is altitude (km)
    pp = compplasmaparam(msis, hd["approx"])

    iono = xarray.Dataset({"msis": msis, "pp": pp}, attrs={"hd": hd})

    msisint, rawinterp = interpdat(iono, dz, raw, newaltmethod)

    writeinterpunformat(msisint.attrs["hd"]["nx"], rawinterp, hdraw, ofn)

    return msisint


def getaltgrid(ifn: Path) -> xarray.DataArray:
    """
    Helper function for HiST-feasibility to quickly get transcar alt grid
    """
    nhead = headbytes // d_bytes
    hd = readionoheader(ifn, nhead)[0]
    msis, raw = readinitconddat(hd, ifn)  # index is altitude (km)

    return msis.alt_km


def interpdat(md: xarray.DataArray, dz, raw: np.ndarray, newaltmethod: str = None) -> tuple:
    """interpolate data to new altitude grid"""
    # %% was interpolation requested?
    if dz is None or newaltmethod is None:
        return md, raw
    # %% interpolate initial conditions
    malt = newaltmethod.lower()
    if malt == "tanh":
        z_new = setupz(md.shape[0], md.index[0], dz[0], dz[1])
    elif malt == "linear":
        print(f"interpolating to grid space {dz:.2f} km.")
        z_new = np.arange(md.index[0], md.index[-1], dz[0], dtype=float)
    elif malt == "incr":
        """
        in this case, dz is start spacing and  amount to increase step size for each element
        The method used to implement this is inefficient, but it is a very small dataset.
        """
        z_new = [md.index[0]]
        cdz = dz[0]
        while (z_new[-1] + cdz) < md.index[-1]:
            z_new.append(z_new[-1] + cdz)
            cdz += dz[0]
        z_new = np.asarray(z_new)
    else:
        logging.error(f"unknown interp method {newaltmethod}, returning unaltered values.")
        return md, raw

    if z_new.size > toobig:
        logging.warning(f"Transcar may not accept altitude grids with more than about {toobig} elements.")

    # %% assemble output
    mint = xarray.DataArray(
        np.empty((z_new.size, md.shape[1])),
        dims=["alt_km", "isrparam"],
        coords={"alt_km": z_new, "isrparam": md.coords["isrparam"]},
    )  # this is faster than list(md)
    for m in md:
        fint = interp1d(md.index, md[m], kind="linear", axis=0)
        mint.loc[:, m] = fint(z_new)
    # %% new header, only change to number of altitudes
    hdint = md.attrs["hd"]
    hdint["nx"] = z_new.size
    # %% raw data, we'll write this to disk later
    fint = interp1d(md.index, raw, kind="linear", axis=0)
    rawint = fint(z_new)
    # %% interpolate derived parameters
    ppint = xarray.DataArray(
        np.empty((z_new.size, md["pp"].shape[1])),
        dims=["alt_km", "isrparam"],
        coords={"alt_km": z_new, "isrparam": md.coords["isrparam"]},
    )
    for p in md["pp"]:
        fint = interp1d(md["pp"].alt_km, md["pp"].loc[:, p], kind="linear", axis=0)
        ppint.loc[:, p] = fint(z_new)

    iono = xarray.Dataset({"md": mint, "pp": ppint}, attrs={"hd": hdint})

    return iono, rawint


def writeinterpunformat(nx: int, rawi, hdraw, ofn: Path = None):
    """write altitude-interpolated data to proprietary Transcar binary format"""

    if ofn is None:
        return

    ofn = Path(ofn).expanduser()
    # update header with new number of altitudes due to interpolation
    hdraw[0] = nx

    print("writing", ofn)
    with ofn.open("wb") as f:
        hdraw.tofile(f, "", "%f32")
        rawi.astype(np.float32).tofile(f, "", "%f32")


def readinitconddat(hd: dict, fn: Path) -> Tuple[xarray.DataArray, np.ndarray]:
    """Reads initial conditions for Transcar from binary file"""
    fn = Path(fn).expanduser()
    nx = hd["nx"]
    ncol = hd["ncol"]

    # *** these indices correspond exactly to the columns of msis!! ****
    # from transconvec_13.op.f lines 452 - 542
    if hd["approx"].astype(int) == 13:
        dextind = tuple(range(1, 34))
    else:
        dextind = tuple(range(1, 13)) + (12, 13, 13, 14, 14, 15, 15, 16, 16) + tuple(range(17, 29))

    if ncol > 60:
        dextind += (60, 61, 62)

    dextind += (49,)  # as in output

    with fn.open("rb") as f:  # python2 requires r first
        ipos = 2 * ncol * d_bytes
        f.seek(ipos, 0)
        rawall = np.fromfile(f, np.float32, nx * ncol).reshape((nx, ncol), order="C")  # yes order='C'!

    msis = xarray.DataArray(
        rawall[:, dextind],
        dims=["alt_km", "isrparam"],
        coords={
            "alt_km": rawall[:, 0],
            "isrparam": [
                "n1",
                "n2",
                "n3",
                "n4",
                "n5",
                "n6",
                "v1",
                "v2",
                "v3",
                "vm",
                "ve",
                "t1p",
                "t1t",
                "t2p",
                "t2t",
                "t3p",
                "t3t",
                "tmp",
                "tmt",
                "tep",
                "tet",
                "q1",
                "q2",
                "q3",
                "qe",
                "nno",
                "uno",
                "po",
                "ph",
                "pn",
                "pn2",
                "po2",
                "heat",
                "po1d",
                "no1d",
                "uo1d",
                "n7",
            ],
        },
        attrs={"filename": fn},
    )

    return msis, rawall


# %% read transcar
def calcVERtc(datadir: Path, tReq: datetime, config_fn: Path):
    """
    calcVERtc is the function called by "hist-feasibility" to get Transcar modeled VER/flux

    outputs:
    --------
    spec: Panel of excitation rates: reaction x altitude x time

    We use pcolormesh instead of imshow to enable correct log-plot labeling/coloring

    References include:
    Zettergren, M. "Model-based optical and radar remote sensing of transport and composition
                    in the auroral ionosphere" PhD Thesis, Boston Univ., 2009
    Zettergren, M. et al "Optical estimation of aurinfileinfileoral ion upflow: 2. A case study"
          JGR Vol 113 A7  2008 DOI:10.1029/2007JA012691
    Zettergren, M. et al "Optical estimation of auroral ion upflow: Theory"
          JGR Vol 112 A12 2007 DOI: 10.1029/2007JA012691

    Tested with:
    Matplotlib 1.4 (1.3.1 does NOT work for pcolormesh)

    Plambda contains all the wavelengths generated for the reactions at a particular beam energy level
    Plambda row: wavelength col: altitude
    for each energy bin, we take Plambda through the EMCCD window and optional BG3 filter,
    yielding Peigen, a ver eigenprofile p(z,E) for that particular energy
    """
    # %% get beam directory
    beamdir = Path(datadir)
    # %% read simulation parameters
    tctime = readTranscarInput(beamdir / "dir.input" / config_fn)
    if tctime is None:
        return

    if tReq is not None:
        if not tctime["tstartPrecip"] < tReq < tctime["tendPrecip"]:
            logging.info(f'precip start/end: {tctime["tstartPrecip"]} / {tctime["tendPrecip"]}')
            logging.error(f"your requested time {tReq} is outside the precipitation time")
            tReq = tctime["tendPrecip"]
            logging.warning(f"falling back to using the end simulation time: {tReq}")
    # %% convert transcar output
    rates = ExcitationRates(beamdir / KINFN)

    tReqInd, tUsed = picktime(rates.time.values, tReq)

    rates = rates[tReqInd, ...]

    return rates


def picktime(tTC, tReq):

    if tReq is None:
        tReqInd = slice(None)
    else:
        tReq = np.datetime64(tReq)
        tReqInd = abs(tTC - tReq).argmin()

    tUsed = tTC[tReqInd]

    return tReqInd, tUsed


# %% for testing only


class SimpleSim:
    """
    simple input for debugging/self test
    """

    def __init__(
        self, filt: str, inpath: Path, reacreq: List[str] = None, lambminmax: Tuple[int, int] = None, transcarutc: datetime = None
    ):
        self.loadver = False
        self.loadverfn = Path("precompute/01Mar2011_FA.h5")
        self.opticalfilter = filt
        self.minbeamev = 0
        self.obsalt_km = 0
        self.zenang = 77.5
        # self.maxbeamev = #future
        self.transcarev = Path(__file__).parent / "../BT_E1E2prev.csv"

        self.excratesfn = "dir.output/emissions.dat"
        self.transcarpath = inpath
        self.transcarconfig = "DATCAR"

        self.transcarutc = transcarutc

        if reacreq is None:
            self.reacreq = ["metastable", "atomic", "n21ng", "n2meinel", "n22pg", "n21pg"]
        else:
            self.reacreq = reacreq

        if lambminmax is None:
            self.lambminmax = (1200, 200)
        else:
            self.lambminmax = lambminmax

        # self.reactionfn = Path('precompute/vjeinfc.h5')
        # self.bg3fn = Path('precompute/BG3transmittance.h5')
        # self.windowfn = Path('precompute/ixonWindowT.h5')
        # self.qefn = Path('precompute/emccdQE.h5')


# %% ISR


def compplasmaparam(iono: xarray.DataArray, approx: int) -> xarray.DataArray:
    assert isinstance(iono, xarray.DataArray)

    pp = xarray.DataArray(
        np.empty((iono.shape[0], 4)),
        coords=[("alt_km", iono.alt_km), ("isrparam", ["ne", "vi", "Ti", "Te"])],
        attrs={"filename": iono.attrs["filename"]},
    )

    nm = iono.loc[:, ["n4", "n5", "n6"]].sum(dim="isrparam")

    pp.loc[:, "ne"] = comp_ne(iono)
    #    pp.sel(isrparam='ne') = comp_ne(iono) # doesn't work for assign?
    pp.loc[:, "vi"] = comp_vi(iono, nm, pp)
    pp.loc[:, "Ti"] = comp_Ti(iono, nm, pp)
    pp.loc[:, "Te"] = comp_Te(iono, approx)

    return pp


def comp_ne(d: xarray.DataArray) -> xarray.DataArray:
    """compute electron density vs. altitude"""
    return d.loc[:, ["n1", "n2", "n3", "n4", "n5", "n6", "n7"]].sum("isrparam")


def comp_vi(d: xarray.DataArray, nm: xarray.DataArray, pp: xarray.DataArray) -> xarray.DataArray:
    """compute ion velocity vs. altitude"""
    return (
        d.loc[:, ["n1", "v1"]].prod("isrparam")
        + d.loc[:, ["n2", "v2"]].prod("isrparam")
        + d.loc[:, ["n3", "v3"]].prod("isrparam")
        + nm * d.loc[:, "vm"]
    ) / pp.loc[:, "ne"]


def comp_Ti(d: xarray.DataArray, nm: xarray.DataArray, pp: xarray.DataArray) -> xarray.DataArray:
    """
    Compute ion temperature
    Refs: transconvec_13.op.f  read_fluidmod.m, data_tra.m
    """

    Tipar = (
        d.loc[:, ["n1", "t1p"]].prod("isrparam")
        + d.loc[:, ["n2", "t2p"]].prod("isrparam")
        + d.loc[:, ["n3", "t3p"]].prod("isrparam")
        + nm * d.loc[:, "tmp"]
    ) / pp.loc[:, "ne"]

    Tiperp = (
        d.loc[:, ["n1", "t1t"]].prod("isrparam")
        + d.loc[:, ["n2", "t2t"]].prod("isrparam")
        + d.loc[:, ["n3", "t3t"]].prod("isrparam")
        + nm * d.loc[:, "tmt"]
    ) / pp.loc[:, "ne"]
    # return (n1*t1 + n2*t2 + n3*t3 +nm*tm)/(n1 +n2 +n3 +nm)
    Ti = (1 / 3) * Tipar + (2 / 3) * Tiperp

    return Ti


def comp_Te(d: xarray.DataArray, approx: int) -> xarray.DataArray:
    if int(approx) == 13:
        Te = (d.loc[:, "tep"] + 2 * d.loc[:, "tet"]).astype(float) / 3.0
    else:
        Te = d.loc[:, "tep"].astype(float)

    return Te


# %%


def ExcitationRates(kinfn: Path) -> xarray.DataArray:
    """
    Michael Hirsch 2014
    Parses the ASCII dir.output/emissions.dat in milliseconds
    based on transconvec_13

    outputs:
    excrate: xarray.DataArray of reaction x altitude x time

    variables:
    ------------
    Nalt: number of altitudes in simulation (not necessarily uniform spacing!)
    nen:
    dipangle,cdip: dip angle of B-field (degrees)
    timeop,ctime: time of simulation step (UTC)
    zop: altitudes [km]
    Nprecip: At the end of each time step, there are this many elements of precipitation data to read
    NprecipCol: 2, this accounts for e and fluxdown (each taking one column)
    NdataCol: number of data elements per altitude + 1
    NumData: number of data elements to read at this time step
    """
    rates = readexcrates(kinfn)
    # breakup slightly to meet needs of simpler external programs
    # z = excite.major_axis.values
    return rates["excitation"]


def initparams(kinfn: Path) -> Tuple[Path, int, int, float, datetime, int, int, int]:
    kinfn = Path(kinfn).expanduser()

    with kinfn.open("r") as fid:  # going to rewind after this priming read
        line = fid.readline()

    ctime, dip, nalt, nen = getHeader(line)

    Nprecip = NprecipCol * nen  # how many precip elements to read at this time step
    ndat = NdataCol * nalt  # how many elements to read at this time step
    # how many rows of data (less header) to read in a batch
    ndatrow = (ndat + Nprecip) // NumPerRow + 1

    logging.debug(f"{kinfn} {ctime} Nalt: {nalt} nen: {nen} dipangle[deg]: {dip:.2f}")

    return kinfn, nalt, nen, dip, ctime, ndatrow, ndat, Nprecip


def readexcrates(kinfn: Path) -> xarray.Dataset:

    kinfn, nalt, nen, dipangle, ctime, ndatrow, ndat, Nprecip = initparams(kinfn)
    # using read_csv was vastly slower!

    with kinfn.open("r") as f:
        dstream = np.asarray(f.read().split()).astype(float)
    # print(time()-tic)
    nhead = NumPerRow
    size_record = ndat + Nprecip + nhead
    n_t = dstream.size // size_record

    t = np.empty(n_t, datetime)
    excrate = xarray.DataArray(np.empty((n_t, nalt, 10)), dims=["time", "alt_km", "reaction"])
    excrate["reaction"] = ["no1d", "no1s", "noii2p", "nn2a3", "po3p3p", "po3p5p", "p1ng", "pmein", "p2pg", "p1pg"]

    precip = xarray.DataArray(data=np.empty((n_t, nen, NprecipCol)), dims=["time", "e", "fluxdown"])

    for i in range(n_t):
        cind = np.s_[i * size_record: (i + 1) * size_record]
        crec = dstream[cind]

        # h = crec[:nhead] #unused
        d = crec[nhead:-Nprecip].reshape((nalt, NdataCol), order="C")
        # blank nan are between data and precip
        p = crec[-Nprecip:].reshape((nen, NprecipCol), order="C")

        t[i] = parseheadtime(crec[:2])

        excrate[i, ...] = d[:, 1:]

        precip[i, ...] = p

    excrate["alt_km"] = d[:, 0]
    excrate["time"] = t

    precip["time"] = t

    rates = xarray.Dataset({"excitation": excrate, "precip": precip})

    return rates


def getHeader(line: str) -> Tuple[datetime, float, int, int]:
    """
    head[0]: Year, day of year YYYYDDD
    head[1]: second of day from midnight UTC
    head[2]: 90 - head[2] = B-field dipangle [deg]
    head[3]: Nalt
    head[4]: nen
    """
    head = line.split(None)  # None: multiple whitespace as one
    assert len(head) == 5
    # dt.strptime(head[0],'%Y%j') + relativedelta(seconds=float(head[1]))
    timeop = parseheadtime(head)
    dipangle = 90.0 - float(head[2])
    nalt = int(head[3])
    nen = int(head[4])

    return timeop, dipangle, nalt, nen


def parseheadtime(h: np.ndarray) -> datetime:
    return datetime.strptime(str(int(h[0])), "%Y%j") + timedelta(seconds=float(h[1]))
