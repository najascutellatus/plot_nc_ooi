# plot-nc-ooi
This is a python script that plots netCDF datasets. 

##Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Scripts](#scripts)
- [Examples](#examples)

###Introduction
This script was created for the Ocean Observatories Initiative (OOI) data review team to quickly plot multiple netCDF files. As of right now, you are able to create timeseries, profiles, and x-y plots. More functionality will be added in the future.


###Installation
    >git clone https://github.com/najascutellatus/plot-nc-ooi.git

There's also a [pip_requirements.txt] containing the required packages.  To install these packages, use:

> pip install -r pip_requirements.txt

###Scripts
There is one main script:
- [plotNC4.py](https://github.com/ooi-integration/uframe-webservices/blob/master/get_arrays.py): Plots a directory of netCDF4 files recursively.

The default argument inputs are:
- [--dir]: Current working directory
- [--sav]: Current working directory
- [--type]: ts (Timeseries plot)
- [--res]: 100 (100 dpi)
- [--linestyle]: '-ro' (Black line connected by red circles)

###Examples

plotNC4 Help Documentation:

> plotNC4.py -h

To make a time series plot of a netCDF4 file,

> plotNC4.py -d /Users/michaesm/OOI/netcdf/ -s /Users/michaesm/OOI/plots/ -p ts 
