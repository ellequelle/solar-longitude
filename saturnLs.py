from io import StringIO
import numpy as np
import pandas as pd

"""
Functions to convert Saturn's solar longitude to and from SCET/UNIX timestamp, datetime, and Julian date.
Written 2021 by LE Hanson
"""


__all__ = [
    'datetime_to_Ls2', 'Ls2_to_datetime', 'datestr_to_Ls2',
    'SCET_to_datetime', 'datetime_to_SCET',
    'SCET_to_Ls2', 'Ls2_to_SCET',
    'JD_to_SCET', 'SCET_to_JD',
    'Ls2_to_Ls', 'Ls2_to_SYLs', 'SYLs_to_Ls2',
    'dfa',
    ]

#ephem_file = "saturn-from-titan-50_70.txt"
ephem_file = "saturn-Ls-50_70.txt"

def Ls2_to_Ls(ls2):
    SY = ls2//360
    return ls2 - 360*SY

def Ls2_to_SYLs(ls2):
    SY = ls2//360 + 1
    return SY, ls2 - 360*(SY-1)

def SYLs_to_Ls2(SY, Ls):
    return (SY-1)*360 + Ls

def scan_ephem(fname):
    import re
    with open(fname, "r") as fin:
        lines = fin.readlines()
    soe = False
    txt = []
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
    return "".join(txt).replace(", ,", ", NaN,")

def parse_ephem(s):
    df = pd.read_csv(StringIO(s), header=0, na_values="n.a.")
    #df.columns = df.columns.str.strip(" ()").str.translate(str.maketrans(" -():","_____")).str.replace("__","_")
    df = df.dropna("columns")
    if "Calendar_Date_TDB" in df:
        df["Calendar_Date_TDB"] = pd.to_datetime(df["Calendar_Date_TDB"].str[6:])
    if "Date_UT_HRMNSCfff" in df:
        df["Date_UT_HRMNSCfff"] = pd.to_datetime(df["Date_UT_HRMNSCfff"])
    return df[[c for c in df.columns if "Unnamed" not in c]]

def make_Ls_df(df):
    lxneg = df.index < np.nonzero((df["App_Lon_Sun"] < 1).values)[0][0]
    dfa = df.set_index("Date_UT_HRMNSCfff")["App_Lon_Sun"].reset_index()
    dfa["Ls2"] = dfa["App_Lon_Sun"]
    dfa["JDUT"] = df.Date_JDUT
    dfa["SCET"] =  (dfa.Date_UT_HRMNSCfff - pd.to_datetime("1970")).dt.total_seconds()
    dfa.loc[lxneg, "Ls2"] += -360
    
    for ix in np.nonzero((dfa["Ls2"].diff().abs() > 300).values)[0]:
        lx = dfa.index >= ix
        dfa.loc[lx, "Ls2"] = dfa.loc[lx, "Ls2"] + 360
    dfa["SY"] = (dfa["Ls2"]//360 + 1).astype('int8') # saturn year

    dfa = dfa.rename(columns={"Date_UT_HRMNSCfff":"date", "App_Lon_Sun":"Ls"})
    return dfa

def load_ephem(fname):
    return make_Ls_df(parse_ephem(scan_ephem(ephem_file)))

def save_csv(df, fname="saturn-Ls.csv"):
    df.drop(columns=["Ls", "SY", "SCET"])[["date", "JDUT", "Ls2"]].\
      to_csv(fname, index=False)
def load_Ls_csv(fname="saturn-Ls.csv"):
    dfa = pd.read_csv(fname, parse_dates=[0], infer_datetime_format=True, cache_dates=False)
    # make SCET
    dfa["SCET"] = (dfa.date - pd.to_datetime("1970")).dt.total_seconds()
    # make SY, Ls
    dfa["SY"], dfa["Ls"] = Ls2_to_SYLs(dfa["Ls2"])
    dfa["SY"] = dfa["SY"].astype('int8')
    return dfa

#dfa = load_ephem(ephem_file)
dfa = load_Ls_csv()

# convert Ls2 and SCET
def SCET_to_Ls2(scet):
    return np.interp(scet, dfa.SCET, dfa.Ls2)
def Ls2_to_SCET(ls2):
    return np.interp(ls2, dfa.Ls2, dfa.SCET)

# convert Ls2 and JD
def JD_to_SCET(jd):
    return np.interp(jd, dfa.JDUT, dfa.SCET)
def SCET_to_JD(scet):
    return np.interp(scet, dfa.SCET, dfa.JDUT)

# convert SCET and datetime
def SCET_to_datetime(scet):
    return pd.to_datetime(scet, unit='s')
def pddt_scet(pddt):
    return (pddt - pd.to_datetime("1970")).total_seconds()
pddt_scet = np.frompyfunc(pddt_scet, nin=1, nout=1) 
def datetime_to_SCET(pdt):
    from datetime import datetime
    if isinstance(pdt, datetime):
        pdt = pdt.replace(tzinfo=None)
    return pddt_scet(pd.to_datetime(pdt))
    #return (pd.to_datetime(pdt.replace(tzinfo=None)) - pd.to_datetime("1970")).total_seconds()
datetime_to_SCET = np.frompyfunc(datetime_to_SCET, nin=1, nout=1) 


# convert datetime and Ls2
def datetime_to_Ls2(pdt):
    return SCET_to_Ls2(datetime_to_SCET(pdt))
    #return (pd.to_datetime(pdt.replace(tzinfo=None)) - pd.to_datetime("1970")).total_seconds()
datetime_to_Ls2 = np.frompyfunc(datetime_to_Ls2, nin=1, nout=1) 
def Ls2_to_datetime(Ls2):
    return SCET_to_datetime(Ls2_to_SCET(Ls2))

# convert date string to Ls
def datestr_to_Ls2(datestr):
    """
    THIS FUNCION IS NOT GOOD....
    I think the issue here is with datetime assuming local time.
    """
    print("The function datestr_to_Ls2 is inaccurate")
    return SCET_to_Ls2(pd.to_datetime(datestr))

#
# horizons@ssd.jpl.nasa.gov
# the funcions in this file use output from NASA Horizons using the following
'''
!$$SOF
COMMAND= '699'
CENTER= '500@606'
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
QUANTITIES= '14,15,19,20,32,41,44'
!$$EOF
'''


