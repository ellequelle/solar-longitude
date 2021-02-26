import numpy as np
import saturnLs
from saturnLs import *
from importlib import reload
reload(saturnLs)

def t1():
    '''datetime_to_Ls2'''
    return (datetime_to_Ls2(dfa.date) - dfa.Ls2)/dfa.Ls2.sum()
def t2():
    '''Ls2_to_datetime'''
    return Ls2_to_datetime(dfa.Ls2) - dfa.date
def t3():
    '''datestr_to_Ls2'''
    return (datestr_to_Ls2(dfa.date.astype(str)) - dfa.Ls2)/dfa.Ls2.sum()
def t4():
    '''SCET_to_datetime'''
    return SCET_to_datetime(dfa.SCET) - dfa.date
def t5():
    '''datetime_to_SCET'''
    return (datetime_to_SCET(dfa.date) - dfa.SCET)/dfa.SCET.sum()
def t6():
    '''SCET_to_Ls2'''
    return (SCET_to_Ls2(dfa.SCET) - dfa.Ls2)/dfa.Ls2.sum()
def t7():
    '''Ls2_to_SCET'''
    return (Ls2_to_SCET(dfa.Ls2) - dfa.SCET)/dfa.SCET.sum()
def t8():
    '''JD_to_SCET'''
    return (JD_to_SCET(dfa.JDUT) - dfa.SCET)/dfa.SCET.sum()
def t9():
    '''SCET_to_JD'''
    return (SCET_to_JD(dfa.SCET) - dfa.JDUT)/dfa.JDUT.sum()
def t10():
    '''Ls2_to_Ls'''
    return (Ls2_to_Ls(dfa.Ls2) - dfa.Ls)/dfa.Ls.sum()
def t11():
    '''Ls2_to_SYLs'''
    sy, ls = Ls2_to_SYLs(dfa.Ls2)
    return np.sqrt((dfa.SY-sy)**2 + (dfa.Ls-ls)**2)/(dfa.SY**2 + dfa.Ls**2).sum()
def t12():
    '''SYLs_to_Ls2'''
    return (SYLs_to_Ls2(dfa.Ls, dfa.SY) - dfa.Ls2)/dfa.Ls2.sum()


def plot_error_SCET_Ls2(ixskip=100, ixoff=0, dfa=dfa):
    import matplotlib.pyplot as plt
    ixbuf = max(ixskip,ixoff)*2
    dfp = dfa.iloc[ixbuf:-ixbuf] # keep all rows
    dfs = dfa.iloc[ixoff::ixskip] # only keep every ixskip rows
    ls2 = SCET_to_Ls2(dfp.SCET, dfa=dfs) # calculate interpolated Ls2
    dLs2 = dfp.Ls2.diff() # daily change in Ls2
    ferr = (ls2-dfp.Ls2)/dLs2
    rms = np.sqrt(np.mean(ferr**2))
    # plot error as fraction of daily change in Ls2
    plt.figure()
    plt.plot(dfp.SCET, ferr, '.', markersize=4)
    plt.title(f"interpolating over {ixskip} days; rms: {rms:0.3g}; max: {np.abs(ferr).max():0.3g}")
    plt.xlabel("SCET [s]")
    plt.ylabel("Ls2 error as fraction of daily $\Delta$Ls2")
    return rms, np.abs(ferr).max()

def plot_error_Ls2_SCET(ixskip=100, ixoff=0, dfa=dfa):
    import matplotlib.pyplot as plt
    ixbuf = max(ixskip,ixoff)*2
    dfp = dfa.iloc[ixbuf:-ixbuf] # keep all rows
    dfs = dfa.iloc[ixoff::ixskip] # only keep every ixskip rows
    scet = Ls2_to_SCET(dfp.Ls2, dfa=dfs) # calculate interpolated SCET
    dSCET = dfp.SCET.diff() # daily change in SCET
    ferr = (scet-dfp.SCET)/dSCET
    rms = np.sqrt(np.mean(ferr**2))
    # plot error as fraction of daily change in SCET
    plt.figure()
    plt.plot(dfp.Ls2, ferr, '.', markersize=4)
    plt.title(f"interpolating over {ixskip} days; rms: {rms:0.3g}; max: {np.abs(ferr).max():0.3g}")
    plt.xlabel("Ls2 [$\degree$]")
    plt.ylabel("SCET error as fraction of daily $\Delta$SCET")
    return ferr

def plot_error_trend(ixoff=0):
    import matplotlib.pyplot as plt
    errs = []
    #ixs = np.concatenate((np.arange(2,10), np.logspace(1,np.log10(600),50).astype(int),[100,200,300]))
    ixs = np.concatenate((np.arange(2,100), np.arange(100,300,2), np.arange(300,750,25)))
    for ix in np.sort(ixs):
        r,x = plot_error_SCET_Ls2(ix, ixoff=ixoff)
        plt.close()
        errs.append((ix,r,x))
    errs = np.array(errs).T
    plt.figure()
    plt.plot(errs[0], errs[1], 'v--', label="rms rel err", markersize=3)
    plt.plot(errs[0], errs[2], 'o--', label="max abs rel err", markersize=3)
    plt.axhline(y=1, color='k', linestyle='-', linewidth=1)
    plt.axhline(y=0.5, color='k', linestyle='--', linewidth=1)
    plt.axhline(y=0.2, color='k', linestyle=':', linewidth=1)
    plt.xlabel('interval')
    plt.ylabel('fractional daily (24 hr) error')
    plt.legend()
    plt.xlim(40,400)
    plt.ylim(0.03,1.4)

def run_tests():
    fcs = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12]
    for func in fcs:
        print(f"{func.__doc__}: ", np.sum(func()))


if __name__ == "__main__":
    run_tests()
