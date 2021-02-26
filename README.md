# saturnLs

saturnLs converts between Saturn solar longitude, Ls, and date. It iterpolates ephemeris output by [JPL HORIZONS](https://ssd.jpl.nasa.gov/?horizons) to convert between Ls and date with an error less than the day-to-day change in Ls. Functions are provided to convert among Ls, Gregorian calendar date, UNIX timestamp, and Julian date.

#### disclaimer
*This grew out of my attempts to understand Saturn's orbit, specifically as it pertains to seasonal weather on Titan, but it is not being actively developed. I am posting this project in the hope that someone else may find it useful. Although I would like to develop this further to be more user-friendly and generalizable, that may never occur.*

*Feel free to contact me if you are interested in contributing or if you have an idea for improvements.*

# definitions
Temporary list of definitions from saturnLs.py:
 * Ls: Solar longitude, apparent longitude of the sun seen from Saturn as defined in JPL Horizons.
 * SY: Saturn year number where SY 1 is the Saturn year starting September 21, 1950.
 * Ls2: Solar longitude since the beginning of SY 1 starting September 21, 1950.
 * SCET: SpaceCraft Event Time (from Cassini), time in seconds since January 1, 1970 (UNIX epoch).
 * JD (or JDUT): Julian Date, UT.
 * datetime: Python datetime object (including numpy datetime64, pandas Timestamp, and astropy Time).
 * datestr (or datestring): Date and/or time as a string.

# usage
Although there are plans to write a command-line tool using saturnLs, it is currently just a python library. Several functions are currently available for converting between Ls and dates, though there are plans to improve the API, possibly based on the [astropy](https://www.astropy.org) `Time` or the [pandas](https://pandas.pydata.org) `Timestamp` types.

## examples
Convert a date string to Ls2:
```python
> datestr = "2005-01-14 13:37:00"
> saturnLs.datestr_to_Ls2(datestr)
array(660.23240127)
```
Convert a date string to Ls (relative to the respective Saturn year):
```python
> saturnLs.datestr_to_Ls(datestr)
300.23240126594817
```
Convert Ls2 to datetime:
```python
> saturnLs.Ls2_to_datetime(660.232)
Timestamp('2005-01-14 13:20:23.619411230')
```
Convert between Ls2 and Saturn year and Ls:
```python
> saturnLs.Ls2_to_SYLs(660.232)
(2.0, 300.23199999999997)
> saturnLs.SYLs_to_Ls2(SY=2, Ls=300.232)
> 660.232
```

# details
Dates are in [Universal Time (UT)](https://ssd.jpl.nasa.gov/?horizons_doc#time), defined in HORIZONS as follows:
> This can mean one of two non-uniform time-scales based on the rotation of the Earth. For this program, prior to 1962, UT means UT1. After 1962, UT means UTC or "Coordinated Universal Time". Future UTC leap-seconds are not known yet, so the closest known leap-second correction is used over future time-spans.

# dependencies
## required
* [numpy](https://numpy.org)
* [pandas](https://pandas.pydata.org)
## optional
* [scipy](https://scipy.org/scipylib/)
Interpolations are done by `scipy.interpolate.interp1d`, and `np.interp` is used as a fallback.

## ephemeris data
saturnLs can work with two different data sources: raw HORIZONS output, or the reduced output saved as a csv file. While the relevant data in both files is identical, the csv file is preferred, as it is significantly smaller and faster to load.

### csv ephemeris
Several of the fields in the DataFrame can be calculated from `date` and `Ls`, so function `load_csv_ephem` is provided to do this when a csv file is loaded.
```python
> df = saturnLs.load_csv_ephem("saturn-Ls-sparse.csv")
> df
           date       JDUT          SCET          Ls2          Ls   SY
0    1890-01-01  2411368.5 -2.524522e+09  -743.278567  336.721433 -2.0
1    1890-03-29  2411455.5 -2.517005e+09  -740.190532  339.809468 -2.0
...         ...        ...           ...          ...         ...  ...
1141 2159-05-28  2509765.5  5.976979e+09  2551.005581   31.005581  8.0
1142 2159-08-23  2509852.5  5.984496e+09  2553.809076   33.809076  8.0

[1143 rows x 6 columns]
```

By default, saturnLs loads the csv file whos path is specified by the variable `ephem_csv`. Included are two csv files that have been reduced from HORIZONS output. Solar longtidue, Gregorian calendar date, and Julian date are tabulated in the files `saturn-Ls-sparse.csv` and `saturn-Ls.csv`, at intervals of 87 days and 12 hours, respectively. An interval of 87 days was chosen to minimize the error in the interpolated Ls (when compared with the 12-hour HORIZONS output). Apparenntly due to oscillations caused by Titan, the interpolation error is very sensitive to the sampling interval.


### loading HORIZONS ouput
saturnLs provides the function `load_ephem` to parse raw HORIZONS output (csv format) and load it into a pandas arrray. To load a new text file conaining HORIZONS output, run the following:
```python
> import saturnLs
> df = saturnLs.load_ephem("saturn-Ls-1970_2040-sol.txt")
> df
                     date       JDUT          SCET          Ls2          Ls   SY
0     1970-01-01 00:00:00  2440587.5  0.000000e+00   224.558213  224.558213  1.0
4     1970-01-03 00:00:00  2440589.5  1.728000e+05   224.633295  224.633295  1.0
...                   ...        ...           ...          ...         ...  ...
51132 2039-12-29 12:00:00  2466152.0  2.208773e+09  1091.520676   11.520676  4.0
51136 2039-12-31 12:00:00  2466154.0  2.208946e+09  1091.587601   11.587601  4.0

[51134 rows x 6 columns]
```
The data loaded into `df` can then be saved using the function `save_csv_ephem` as follows:
```python
> saturnLs.save_csv_ephem(df, fname="saturn-Ls.csv")
```
This saves a csv file with the `date`, `JDUT`, and `Ls` columns.
