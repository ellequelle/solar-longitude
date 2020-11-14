from numpy import sin, cos
from numpy.polynomial import Polynomial

"""
Functions to calculate solar longitude at Saturn from UNIX timestamp or Julian Date.
Written 2020 by LE Hanson
"""

# fit parameters
unix_to_Ls_coef0 = (718.6900125511373, 774.1305095617424, -0.8446076817777325,
                        5.625920617250136, 2.3096357989383614, -12.987278185298077,
                        -1.3977724796575686, 12.802556973961142, -0.19768056277896529,
                        -4.694767647649146)
unix_to_Ls_domain = (-1, 1)
unix_to_Ls_cos_params = ( 0.07393232, -0.17575192,  6.2167401 )
unix_to_Ls_sin_params = ( 0.03684395, -0.36251834, -0.19146985 )


# polynomial terms
unix_to_Ls_fp = Polynomial(unix_to_Ls_coef0, domain=unix_to_Ls_domain)


# cosine and sine terms
def costerm(xx):
    return unix_to_Ls_cos_params[2]*cos( xx/unix_to_Ls_cos_params[0] + unix_to_Ls_cos_params[1] )

def sinterm(xx):
    return unix_to_Ls_sin_params[2]*sin( xx/unix_to_Ls_sin_params[0] + unix_to_Ls_sin_params[1] )


# Function to calculate the Saturn solar longitude from the normalized date
def xx_to_Ls(xx):
    "Calculate Saturn solar longitude from normalized date."
    ls0 = unix_to_Ls_fp(xx)
    ls1 = costerm(xx)
    ls2 = sinterm(xx)
    return ls0 + ls1 + ls2


# Functions to normalize Julian date and Unix time
def UNIX_to_xx(unix):
    "Normalize Unix time"
    return unix*5e-10 - 1262304000*5e-10

def JD_to_xx(JD):
    "Normalize Julian date"
    return 4.32e-5*JD - 105.43338 - 0.631152


# Functions to calculate Saturn solar longitude from the Julian date and Unix time
def UNIX_to_Ls(unix):
    '''
    Calculate the solar longitude from Unix time (seconds from January 1, 1970).
    '''
    return xx_to_Ls(UNIX_to_xx(unix))

def JD_to_Ls(JD):
    '''
    Calculate the solar longitude from Julian Date.
    '''
    return xx_to_Ls(JD_to_xx(JD))


