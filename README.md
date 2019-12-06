# AFAD-Mass-Data-Downloader

A code for downloading information about earthquakes along with the waveforms (optional) 
from Disaster and Emergency Management Presidency ([AFAD](http://kyhdata.deprem.gov.tr/2K/kyhdata_v4.php)). 

Information about the stations and recorded earthquakes can be found in http://kyhdata.deprem.gov.tr/2K/kyhdata_v4.php

Inputs of the search are:

inputs: input parameters file
output_test: name of folder that the search results are stored. If it is empty, time of the search will be used as a folder name.

search_results: True = earthquake catalog will be stored as a .csv file inside the result folder.

earthquake_results: True = station parameters (Distance, PGA, PGV etc.) will be stored inside a subfolder of the earthquake inside the result folder.

get_data: True = waveforms will be downloaded inside the earthquake subfolder(s).

Input parameters should be given as a text file. Inputs can be seen in below:

# Input

Start Date (Format= DD/MM/YYYY). Oldest Date: 01/01/1976

End Date (Format= DD/MM/YYYY)

Epi. Lat. between (eg. 34.00-43.00 *MIN TO MAX)

Epi. Lon. between (eg. 24.00-45.82 *MIN TO MAX)

Depth (km) between (eg. 5.00 - 50.00 *MIN TO MAX)

MD between (eg. 2.3-4.55 *MIN TO MAX)

ML between (eg. 2.3-4.55 *MIN TO MAX)

MS between (eg. 2.3-4.55 *MIN TO MAX)

MW between (eg. 2.3-4.55 *MIN TO MAX)

MB between (eg. 2.3-4.55 *MIN TO MAX)

* AFAD mostly calculates ML. However, if MW is calculated, ML is not given. Beware of this fact and provide the minimum limit of ML and MW.
* Search engine of AFAD do not provide earthquakes for a single day. Do not fill the start and end date with the same date.

# Text to SAC

Downloaded waveforms can be converted by using text2sac.py

Usage:

python text2sac.py -o output_dir filename(s)

# Dependancies

AFAD Mass Downloader has dependancies on the following packages:

[mechanize](https://pypi.org/project/mechanize/), 
[requests](https://pypi.org/project/requests/), 
[pandas](https://pypi.org/project/pandas/), 
[bs4](https://pypi.org/project/bs4/)

Text to SAC has dependancies on the following packages:

[numpy](https://pypi.org/project/numpy/), 
[obspy](https://github.com/obspy/obspy/wiki)

AFAD Mass Downloader and Text to SAC work in Python 3.x.

