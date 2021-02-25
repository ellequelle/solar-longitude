import numpy as np
from saturnLs import *

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
    return (SYLs_to_Ls2(dfa.SY, dfa.Ls) - dfa.Ls2)/dfa.Ls2.sum()

fcs = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12]
for func in fcs:
    print(f"{func.__doc__}: ", np.sum(func()))
