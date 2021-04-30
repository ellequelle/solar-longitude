from io import StringIO
import numpy as np
import pandas as pd

__doc__ = """
Functions to convert Saturn's solar longitude to and from SCET/UNIX timestamp, datetime, and Julian date.

Values:
 * Ls: Solar longitude, apparent longitude of the sun seen from Saturn as defined in JPL Horizons.
 * SY: Saturn year number where SY 1 is the Saturn year starting September 21, 1950.
 * Ls2: Solar longitude since the beginning of SY 1 starting September 21, 1950.
 * SCET: Time in seconds since January 1, 1970 (UNIX epoch).
 * JD (or JDUT): Julian Date, UT.
 * datetime: Python datetime object (including numpy datetime64, pandas Timestamp, and astropy Time).
 * datestr (or datestring): Date and/or time as a string.

Written 2021 by LE Hanson.
"""

_HAS_SCIPY = True
try:
    from scipy.interpolate import interp1d
except:
    _HAS_SCIPY = False


__all__ = [
    'datetime_to_Ls2', 'Ls2_to_datetime', 'datestr_to_Ls2', 'datestr_to_Ls',
    'SCET_to_datetime', 'datetime_to_SCET',
    'SCET_to_Ls2', 'Ls2_to_SCET',
    'JD_to_SCET', 'SCET_to_JD',
    'Ls2_to_Ls', 'Ls2_to_SYLs', 'SYLs_to_Ls2',
    'dfa',
    ]

# calendar and JD date of start of several "Saturn years"
_sy_list = dict((
    (-1, {"date":"1891-10-30 07:07:31.777902603", "JDUT":2412035.7968955776}),
    (0,  {"date":"1921-04-12 00:26:22.458478928", "JDUT":2422791.5183154917}),
    (1,  {"date":"1950-09-21 19:02:40.934159994", "JDUT":2433546.2935293308}),
    (2,  {"date":"1980-03-03 16:12:43.076112986", "JDUT":2444302.175498566}),
    (3,  {"date":"2009-08-11 02:04:21.114835262", "JDUT":2455054.5863554957}),
    (4,  {"date":"2039-01-22 19:51:53.897613049", "JDUT":2465811.327707148}),
    (5,  {"date":"2068-06-29 08:45:54.395126820", "JDUT":2476561.8652129066}),
    (6,  {"date":"2097-12-13 07:54:47.293023586", "JDUT":2487320.82971404}),
    (7,  {"date":"2127-05-21 00:44:11.711929321", "JDUT":2498070.53069111}),
    (8,  {"date":"2156-11-05 03:52:56.824035645", "JDUT":2508831.661768797}),
    ))

# DataFrame holding the date each "Saturn year" begins
dfsy = pd.DataFrame.from_dict(_sy_list, orient='index').rename_axis(index="SY")
dfsy['date'] = pd.to_datetime(dfsy['date'])

# ephemeris files from JPL Horizons
ephem_file_coarse = "saturn-Ls-1890_2160-sol_sparse.txt"
ephem_file_fine = "saturn-Ls-1970_2040-sol.txt"
# define default horizons output file to load
ephem_file = ephem_file_coarse

# csv ephemeris files, reduced from Horizons output
ephem_csv_long = "saturn-Ls-1890_2160-sol_sparse.csv"
ephem_csv_coarse = "saturn-Ls-sparse.csv"
ephem_csv_fine = "saturn-Ls.csv"
# define default csv file to load
ephem_csv = ephem_csv_fine

###################################
# Independent conversion functions
###################################

# these functions do not rely on the ephemeris data

# Ls2 and Ls, SY
def Ls2_to_Ls(ls2):
    '''Convert Ls2 to Ls.'''
    SY = ls2//360
    return ls2 - 360*SY

def Ls2_to_SYLs(ls2):
    '''Convert Ls2 to "Saturn year" SY and Ls.'''
    SY = ls2//360 + 1
    return SY, ls2 - 360*(SY-1)

def SYLs_to_Ls2(Ls, SY=3):
    '''Convert "Saturn year" SY and Ls to Ls2.'''
    return (SY-1)*360 + Ls


# convert SCET and datetime
def SCET_to_datetime(scet):
    '''Convert SCET (seconds since UNIX epoch) to datetime'''
    return pd.to_datetime(scet, unit='s')

def pddt_scet(pddt):
    '''Convert python datetime to SCET.
    This function strips any timezone information.'''
    return (pddt - pd.to_datetime("1970")).total_seconds()
pddt_scet = np.frompyfunc(pddt_scet, nin=1, nout=1) 

def datetime_to_SCET(pdt):
    '''Convert datetime to SCET'''
    from datetime import datetime
    if isinstance(pdt, datetime):
        pdt = pdt.replace(tzinfo=None)
    return pddt_scet(pd.to_datetime(pdt))
datetime_to_SCET = np.frompyfunc(datetime_to_SCET, nin=1, nout=1) 


###########################
# Ephemeris file functions
###########################

def scan_ephem(fname, header=False):
    '''Scan a JPL Horizons ephemeris file (csv format) and return the csv data.'''
    import re, gzip
    if fname.endswith('.gz'):
        with gzip.open(fname,  "rb") as fin:
            lines = []
            for line in fin.readlines():
                lines.append(line.decode())
    else:
        with open(fname, "r") as fin:
            lines = fin.readlines()
    soe = False
    txt, hed = [], []
    for ix in range(len(lines)):
        ll = lines[ix]
        if "$$SOE" in ll:
            cols = lines[ix-2]
            cols = cols.replace(" ","").replace("n.a.","NaN") 
            cols = re.sub(",(\d[^,]+)", r",x\1", re.sub("[*\-]|_+", "_", re.sub("[%()./:]", "" ,cols)))
            txt.append(cols)
            soe = True
        elif "$$EOE" in ll:
            soe = False
        elif soe:
            txt.append(ll.replace(", ,", ", NaN,"))
        elif header and ll[0] !=  '*':
            hed.append(ll)
    csv = "".join(txt).replace(", ,", ", NaN,")
    if header:
        return csv, "".join(hed)
    return csv

def parse_ephem(s):
    """Parse the csv portion of JPL Horizon output (from scan_ephem) and return as a pandas DataFrame."""
    df = pd.read_csv(StringIO(s), header=0, na_values="n.a.")
    df = df.dropna("columns")
    if "Calendar_Date_TDB" in df:
        df["Calendar_Date_TDB"] = pd.to_datetime(df["Calendar_Date_TDB"].str[6:])
    if "Date_UT_HRMNSCfff" in df:
        df["Date_UT_HRMNSCfff"] = pd.to_datetime(df["Date_UT_HRMNSCfff"])
    if "x1_way_down_LT" in df:
        df["x1_way_down_LT"] = pd.to_timedelta(df["x1_way_down_LT"], 'min')
        df = df.rename(columns={"x1_way_down_LT":"one_way_LT"})
    return df[[c for c in df.columns if "Unnamed" not in c]]


def adjust_LT(df):
    """Account for light time.
    Adjust for distance of observer to Saturn using the column "one_way_LT"."""
    dfa = df.copy()
    lt = dfa['one_way_LT'] # one-way light time
    # calculate JDUT adjusted for light time
    jdnew = dfa['JDUT'] - lt.dt.total_seconds()/86400 # correction to JDUT
    ls2 = dfa["Ls2"]

    # interpolate Ls2
    if _HAS_SCIPY:
        finterp = interp1d(jdnew, ls2, kind='linear', fill_value='extrapolate')
        ls2new = finterp(dfa["JDUT"]) # calculate interpolated Ls2
    else:
        ls2new = np.interp(dfa["JDUT"], jdnew, ls2)
    dls2 = ls2new - ls2 # difference in original Ls2 and new Ls2
    dfa["Ls2"] = ls2new # replace Ls2 with corrected values
    dfa["Ls"] += dls2 # correct Ls
    # remove any nan's due to interpolation
    dfa = dfa.dropna(subset=["Ls2", "Ls"])
    # return without one_way_LT
    return dfa.drop(columns=['one_way_LT'])


def make_df_Ls2SY(df):
    """Calculate Ls2, SY, and SCET, referenced from "Saturn year" zero starting in 1921.
    Input is a DataFrame including fields ['date', 'JDUT', 'Ls']."""
    _dfsy = dfsy.copy()
    _dfsy["Ls"] = 0.0
    dfa = pd.concat((df.copy(), _dfsy.reset_index())).sort_values('JDUT')
    dfa["SY"] = dfa["SY"].ffill()
    # if beyond SY table, estimate year
    # could use Ls to find actual start of year but this is easy
    if np.any(dfa.JDUT < dfsy.JDUT.min()) or np.any(dfa.JDUT > dfsy.JDUT.max()+10750):
        jdsy0 = 2433546.2935293308 # SY 0 julian date
        jdyear = 10755 # julian days in saturn year
        lx = (dfa.JDUT < dfsy.JDUT.min()) | (dfa.JDUT > dfsy.JDUT.max()+10750)
        # estimate SY
        dfa.loc[lx, "SY"] = np.floor((dfa.loc[lx, "JDUT"] - jdsy0)/jdyear) + 1
    dfa = dfa.set_index('JDUT').truncate(df.JDUT.min(), df.JDUT.max()).reset_index()
    #dfa = dfa.dropna(thresh=2).reset_index(drop=True)
    dfa["Ls2"] = dfa["Ls"] + 360*(dfa["SY"]-1)
    dfa["SCET"] = (dfa.date - pd.to_datetime("1970")).dt.total_seconds()
    # remove Ls = 0 rows
    dfa = dfa.loc[~dfa["JDUT"].isin(dfsy["JDUT"])]
    # adjust for light time if column "one_way_LT" is present
    if 'one_way_LT' in dfa:
        dfa = adjust_LT(dfa) # adjust_LT removes "one_way_LT" column
    return dfa[['date','JDUT','SCET','Ls2','Ls','SY']]


def make_Ls_df2(df):
    """Make the reference DataFrame from the ephemeris DataFrame."""
    df = df.rename(columns={"Date_UT_HRMNSCfff":"date",
                                 "App_Lon_Sun":"Ls",
                                 "Date_JDUT":"JDUT"})
    return make_df_Ls2SY(df)

def load_ephem(fname=ephem_file):
    '''load JPL HORIZONS csv output as a DataFrame'''
    return make_Ls_df2(parse_ephem(scan_ephem(fname)))

def save_csv_ephem(df, fname="saturn-Ls.csv", keep_date=False):
    '''Save ephemeris DataFrame as a csv file.
    This file loads significantly faster and is smaller than the raw Horizons output.'''
    keepcols = ["JDUT", "Ls"]
    if keep_date:
        keepcols.insert(0, "date")
    df[keepcols].to_csv(fname, index=False)
      
def load_csv_ephem(fname=ephem_csv):
    '''Loads the ephemeris csv file saved by `save_csv_ephem`.'''
    dfa = pd.read_csv(fname)
    dfa["date"] = pd.to_datetime(dfa["JDUT"], unit='D', origin='julian')
    return make_df_Ls2SY(dfa)


# load the ephemeris data (Horizons output or csv)
# this DataFrame is used in all of the Ls-time conversion functions by default
#dfa = load_ephem(ephem_file)
class dfa_store:
    data = None
    
dfa = dfa_store()
dfa.data = load_csv_ephem()

#######################
# conversion functions
#######################


# convert Ls2 and SCET
def SCET_to_Ls2(scet, dfa=dfa):
    """Convert SCET to Ls2."""
    if np.any(scet > dfa.data.SCET.max()) or np.any(scet < dfa.data.SCET.min()):
        raise ValueError("SCET outside of range in data table.")
    # interpolate Ls2
    if _HAS_SCIPY:
        return interp1d(dfa.data.SCET, dfa.data.Ls2, kind='linear')(scet)
    return np.interp(scet, dfa.data.SCET, dfa.data.Ls2)

def Ls2_to_SCET(ls2, dfa=dfa):
    """Convert Ls2 to SCET."""
    if np.any(ls2 > dfa.data.Ls2.max()) or np.any(ls2 < dfa.data.Ls2.min()):
        raise ValueError("Ls2 outside of range in data table.")
    # interpolate SCET
    if _HAS_SCIPY:
        return interp1d(dfa.data.Ls2, dfa.data.SCET, kind='linear')(ls2)
    return np.interp(ls2, dfa.data.Ls2, dfa.data.SCET)


# convert Ls2 and JD
def JD_to_SCET(jd, dfa=dfa):
    """Convert JD to SCET."""
    if np.any(jd > dfa.data.JDUT.max()) or np.any(jd < dfa.data.JDUT.min()):
        raise ValueError("JD outside of range in data table.")
    # interpolate SCET
    if _HAS_SCIPY:
        return interp1d(dfa.data.JDUT, dfa.data.SCET, kind='linear')(jd)
    return np.interp(jd, dfa.data.JDUT, dfa.data.SCET)

def SCET_to_JD(scet, dfa=dfa):
    """Convert SCET to JD."""
    if np.any(scet > dfa.data.SCET.max()) or np.any(scet < dfa.data.SCET.min()):
        raise ValueError("SCET outside of range in data table.")
    # interpolate JD
    if _HAS_SCIPY:
        return interp1d(dfa.data.SCET, dfa.data.JDUT, kind='linear')(scet)
    return np.interp(scet, dfa.data.SCET, dfa.data.JDUT)


# convert datetime and Ls2
def datetime_to_Ls2(pdt):
    """Convert datetime to Ls2."""
    return SCET_to_Ls2(datetime_to_SCET(pdt))
datetime_to_Ls2 = np.frompyfunc(datetime_to_Ls2, nin=1, nout=1)

def datetime_to_SYLs(pdt):
    """Convert datetime to (SY, Ls)."""
    return Ls2_to_SYLs(SCET_to_Ls2(datetime_to_SCET(pdt)))
datetime_to_SYLs = np.frompyfunc(datetime_to_SYLs, nin=1, nout=2) 

def datetime_to_Ls(pdt):
    """Convert datetime to Ls and SY."""
    sy, ls = datetime_to_SYLs(pdt)
    return ls
datetime_to_Ls = np.frompyfunc(datetime_to_Ls, nin=1, nout=1) 


def Ls2_to_datetime(Ls2):
    """Convert Ls2 to datetime."""
    return SCET_to_datetime(Ls2_to_SCET(Ls2))

def SYLs_to_datetime(ls, sy=3, dfa=dfa):
    """Convert SY and Ls to daetime."""
    return SCET_to_datetime(Ls2_to_SCET(SYLs_to_Ls2(ls, sy)))


# convert date string to Ls
def datestr_to_Ls2(datestr):
    """Convert datestring to Ls2."""
    return datetime_to_Ls2(pd.to_datetime(datestr))

def datestr_to_Ls(datestr, include_SY=False):
    """Convert datestring to Ls.
    Returns Ls alone, or (SY, Ls) if include_SY is True."""
    sy, ls = Ls2_to_SYLs(datestr_to_Ls2(datestr))
    if include_SY:
        return sy, ls
    return ls




#
# horizons@ssd.jpl.nasa.gov
# the funcions in this file use output from NASA Horizons using the following
'''
!$$SOF
COMMAND= '699'
CENTER= '500@10'
MAKE_EPHEM= 'YES'
TABLE_TYPE= 'OBSERVER'
START_TIME= '1950-01-01'
STOP_TIME= '2070-01-01'
STEP_SIZE= '1 d'
CAL_FORMAT= 'BOTH'
TIME_DIGITS= 'FRACSEC'
ANG_FORMAT= 'DEG'
OUT_UNITS= 'KM-S'
RANGE_UNITS= 'KM'
APPARENT= 'AIRLESS'
SUPPRESS_RANGE_RATE= 'NO'
SKIP_DAYLT= 'NO'
EXTRA_PREC= 'NO'
R_T_S_ONLY= 'NO'
REF_SYSTEM= 'J2000'
CSV_FORMAT= 'YES'
OBJ_DATA= 'YES'
QUANTITIES= '21,44'
!$$EOF
'''


if __name__ == '__main__':
    import argparse, re

    parser = argparse.ArgumentParser()#exit_on_error=False)
    parser.add_argument('-S', '--saturn-year', nargs=1, help="provide SY argument")
    parser.add_argument('-j', '--julian', help="use Julian date", action='store_true')
    parser.add_argument('-s', '--simple', help='simple output', action='store_true')
    parser.add_argument('-x', '--extended', help='extended date range (1890 to 2160)', action='store_true')
    parser.add_argument('date', nargs='*', help="earth date or Ls", default=['now'], metavar='date_or_Ls')

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_help()

    if args.extended:
        dfa.data = load_csv_ephem(ephem_csv_long)

    for date in args.date:
        outpt = ''
        # check if date is formatted like Ls
        if re.match(r'\A[+-]*\d+[.]*\d*\Z', date):
            if args.saturn_year is not None:
                SY = int(args.saturn_year[0])
            else:
                SY, _ = datestr_to_Ls('now', include_SY=True)
            Ls = date
            date = SYLs_to_datetime(ls=float(Ls), sy=float(SY))
            if args.julian:
                date = f'{date.to_julian_date():f}'
            outpt = f"{date}"
            if not args.simple:
                outpt = f" Date(SY {int(SY):d}, {float(Ls):g}°) = {date}"
        else:
            if args.saturn_year is not None:
                print("Option -S only applies when calculating Earth dates.")
                parser.exit()
            if args.julian:
                date = pd.to_datetime(date, unit='D', origin='julian')
            SY, Ls = datestr_to_Ls(date, include_SY=True)
            outpt = f"{int(SY):d} {Ls:g}"
            if not args.simple:
                outpt = f" Ls({date}) = SY {int(SY):d}, {Ls:g}°"
        print(outpt)
