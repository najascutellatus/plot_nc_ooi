#! /usr/local/bin/python

"""
Created on Thu Feb 11 2016

@author: lgarzio
"""

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import os
import numpy as np
import re
import datetime

'''
This script is used to generate timeseries plots from netCDF or ncml files, between a time range specified by the user.
'''

ncml = 'http://opendap.oceanobservatories.org/thredds/dodsC/rest-in-class/Coastal_Endurance/CE05MOAS/05-CTDGVM000/telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml'
save_dir = '/Users/lgarzio/Documents/OOI/DataReviews/restinclass/Endurance'

# enter deployment dates
start_time = datetime.datetime(2014, 04, 01, 0, 0, 0)
end_time = datetime.datetime(2014, 05, 29, 0, 0, 0)

f = xr.open_dataset(ncml)
f = f.swap_dims({'obs':'time'})

# Select only the time range indicated
f_slice = f.sel(time=slice(start_time,end_time))

global fName
head, tail = os.path.split(ncml)
fName = tail.split('.', 1)[0]
title = fName[0:27]
platform1 = title.split('-')[0]
platform2 = platform1 + '-' + title.split('-')[1]
method = fName.split('-')[-1]

def createDir(newDir):
    # Check if dir exists.. if it doesn't... create it. From Mike S
    if not os.path.isdir(newDir):
        try:
            os.makedirs(newDir)
        except OSError:
            if os.path.exists(newDir):
                pass
            else:
                raise

# Get the time variable
time = f_slice['time'].data

# Identifies variables to skip when plotting
misc_vars = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc',  'time', 'mission', 'obs']
reg_ex = re.compile('|'.join(misc_vars))

sci_vars = [s for s in f.variables if not reg_ex.search(s)]

for v in sci_vars:
    print v

    y_var = f_slice.variables[v]
    y_data = y_var.data

    # Skips the rest of the script if there are no unique values (e.g., array of nans)
    #if len(np.unique(y_data)) == 1:
    #    print "One value. Continuing"
    #    continue

    # Skips the rest of the script if there is no unit attribute for the variable
    try:
        y_units = f_slice[v].units
    except AttributeError:
        y_units = ""
        continue

    try:
        ymin = np.nanmin(y_data)
    except TypeError:
        ymin = ""
        continue

    try:
        ymax = np.nanmax(y_data)
    except TypeError:
        ymax = ""
        continue

    fig, ax = plt.subplots()
    plt.grid()
    plt.margins(y=.1, x=.1)
    try:
        #plt.scatter(time, y_data, c='r', marker='o', lw = .25)
        plt.plot(time, y_data, c='r', marker='o', lw = .75)
    except ValueError:
        print 'x and y must be the same size'
        continue

    # Format date axis
    df = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(df)
    fig.autofmt_xdate()
    #plt.xticks(rotation='vertical')

    # Format y-axis to disable offset
    y_formatter = ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)

    # Labels
    ax.set_ylabel(f[v].name + " ("+ y_units + ")")
    ax.set_title(fName, fontsize=9)
    ax.legend(["Max: %f" % ymax + "\nMin: %f" % ymin], loc='best', fontsize=8)

    filename = fName + "_" + v
    dir1 = os.path.join(save_dir, platform1, platform2, title, "simple_timeseries", method)
    createDir(dir1)
    save_file = os.path.join(dir1, filename)  # create save file name
    plt.savefig(str(save_file),dpi=150) # save figure
    plt.close()