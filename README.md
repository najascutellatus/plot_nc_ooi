# plot-nc-ooi
This toolbox contains python scripts that plot netCDF datasets. 

##Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Scripts](#scripts)
- [Examples](#examples)

###Introduction
This script was created for the Ocean Observatories Initiative (OOI) data review team to quickly plot multiple netCDF files. As of right now, you are able to create timeseries, profiles, and x-y plots. More functionality will be added in the future.


###Installation
    >git clone hhttps://github.com/ooi-data-review/plot-nc-ooi.git

There's also a [requirements.txt] (https://github.com/ooi-data-review/plot-nc-ooi/blob/master/requirements.txt) containing the required packages.  To install these packages, use:

> pip install -r requirements.txt

###Scripts
There is one main script:
- [plot_timeseries.py](https://github.com/ooi-data-review/plot-nc-ooi/blob/master/plot_timeseries.py): Plots a directory of netCDF4 files recursively.

The default argument inputs are:
- [FILES]: url to an .nc/.ncml file or the path to a text file containing .nc/.ncml links. A # at the front will skip links in the text file.
- [OUT]: Directory to save plots

###Examples

plot_timeseries Help Documentation:

> python -m plot_timeseries --help

To make a time series plot of a netCDF4 file,

> python -m plot_timeseries ./thredds-links.txt ./plots
