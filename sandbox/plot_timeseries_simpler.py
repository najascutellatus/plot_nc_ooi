#! /usr/local/bin/python

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import os
import numpy as np
import re
import datetime
import sys

'''
This script is used to generate timeseries plots from netCDF or ncml files, between a time range specified by the user.
'''

# specify input and output
files = '/Users/knuth/Desktop/PREST/files/*.nc'
out = '/Users/knuth/Desktop/PREST/plots'


# enter desired plotting time frame and standard deviation of outliers to reject
start_time = datetime.datetime(2016, 10, 06, 0, 0, 0)
end_time = datetime.datetime(2017, 1, 21, 0, 0, 0)
stdev = 3


# identify variables to skip when plotting
misc_vars = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc',  'time', 'mission', 'obs',
            'volt', 'ref', 'sig', 'amp', 'rph', 'calphase', 'phase', 'therm']
reg_ex = re.compile('|'.join(misc_vars))





def createDir(newDir):
    # Check if dir exists.. if it doesn't... create it.
        try:
            os.makedirs(newDir)
        except OSError:
            if os.path.exists(newDir):
                pass
            else:
                raise

def reject_outliers(data, m=3):
    # function to reject outliers beyond 3 standard deviations of the mean.
    # data: numpy array containing data
    # m: the number of standard deviations from the mean. Default: 3
    return abs(data - np.nanmean(data)) < m * np.nanstd(data)

def plot_timeseries(t, y, ymin, ymax, t0, t1, args):

    yD = y.data

    fig, ax = plt.subplots()
    plt.grid()
    plt.margins(y=.1, x=.1)
    plt.scatter(t, yD, marker='.',lw=.2)
    plt.tight_layout()

    # Format start and end timestamps, t0 and t1, for legend
    t_min = str(t0)
    t_max = str(t1)
    t_min = t_min[:13]
    t_max = t_max[:13]

    # Format date axis
    # df = mdates.DateFormatter('%Y-%m-%d')
    # ax.xaxis.set_major_formatter(df)
    # fig.autofmt_xdate()

    # http://matplotlib.org/api/dates_api.html#matplotlib.dates.AutoDateLocator
    mdates.AutoDateLocator(3)

    # Format y-axis to disable offset
    y_formatter = ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)

    # Labels
    ax.set_ylabel(args[1] + " ("+ y.units + ")")
    ax.set_title(args[0], fontsize=9)
    # ax.legend(["Min: %f" % ymin + "\nMax: %f" % ymax + "\nTMin: %s" % t_min + "\nTMax: %s" % t_max + "\nOutliers: %s" % outliers], loc='best', fontsize=5)
    ax.legend(["Min: %f" % ymin + "\nMax: %f" % ymax + "\nTMin: %s" % t_min + "\nTMax: %s" % t_max], loc='best', fontsize=5)

    filename = args[0] + "_" + args[1]
    save_file = os.path.join(args[2], filename)  # create save file name
    plt.savefig(str(save_file),dpi=150) # save figure
    plt.close()


def mk_str(attrs, str_type='t'):
    """
    make a string of either 't' for title. 's' for file save name.
    """
    site = attrs['subsite']
    node = attrs['node']
    sensor = attrs['sensor']
    stream = attrs['stream']

    if str_type is 's':
        string = site + '-' + node + '-' + sensor + '-' + stream + '-'
    else:
        string = site + '-' + node + '\nStream: ' + stream + '\n' + 'Variable: '
    return string



print files
f = xr.open_mfdataset(files)
f = f.swap_dims({'obs':'time'})
f_slice = f.sel(time=slice(start_time,end_time)) # select only deployment dates provided
fN = f_slice.source

stream = f.stream  # List stream name associated with the data
title_pre = mk_str(f.attrs, 't')  # , var, tt0, tt1, 't')
save_pre = mk_str(f.attrs, 's')  # , var, tt0, tt1, 's')
platform = f.subsite
node = f.node
sensor = f.sensor
save_dir = os.path.join(out, f.subsite, f.node, f.stream, 'timeseries')
createDir(save_dir)

global fName
head, tail = os.path.split(files)
fName = tail.split('.', 1)[0]
title = fName[0:27]

t = f_slice['time'].data
t0 = t[0] # first timestamp
t1 = t[-1] # last timestamp



varList = []
for vars in f_slice.variables:
    varList.append(str(vars))

# for i in varList:
#     print i

yVars = [s for s in varList if not reg_ex.search(s)]

for v in yVars:
    print v
    y = f_slice[v]
    # print y

    # if stdev is None:
    #     y = y
    #     outlier_text = ''
    # else:
    #     ind = reject_outliers(y, stdev)
    #     y = y[ind]
    #     t = t[ind]
    #     outliers = str(len(ind) - sum(ind))
    #     # outlier_text = 'n removed $\pm$ {}$\sigma: $ {}'.format(stdev, outliers)

    yD = y.data

    try:
        ymin = np.nanmin(yD)
    except TypeError:
        ymin = ""
        continue

    try:
        ymax = np.nanmax(yD)
    except TypeError:
        ymax = ""
        continue

    plotArgs = (fName, v, save_dir)
    plot_timeseries(t, y, ymin, ymax, t0, t1, plotArgs)


