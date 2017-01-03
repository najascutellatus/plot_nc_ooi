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
import datetime

'''
This script is used to generate timeseries plots from netCDF or ncml files, between a time range specified by the user.
'''



# specify input and output
urls = ['/Users/knuth/Downloads/deployment0003_RS03AXBS-LJ03A-12-CTDPFB301-streamed-ctdpf_optode_sample_20160915T183110.280201-20160916T003109.985797.nc']
save_dir = '/Users/knuth/Downloads/'




# enter desired plotting time frame
start_time = datetime.datetime(2016, 9, 15, 00, 0, 0)
end_time = datetime.datetime(2016, 9, 15, 23, 0, 0)




# Identifies variables to skip when plotting
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

def plot_timeseries(t, y, ymin, ymax, t0, t1, args):

    yD = y.data

    fig, ax = plt.subplots()
    plt.grid()
    plt.margins(y=.1, x=.1)
    plt.scatter(t, yD, marker='.',lw=.2)

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
    ax.legend(["Min: %f" % ymin + "\nMax: %f" % ymax + "\nTMin: %s" % t_min + "\nTMax: %s" % t_max], loc='best', fontsize=5)

    filename = args[0] + "_" + args[1]
    save_file = os.path.join(args[2], filename)  # create save file name
    plt.savefig(str(save_file),dpi=150) # save figure
    plt.close()




for url in urls:
    print url
    f = xr.open_dataset(url)
    f = f.swap_dims({'obs':'time'})
    f_slice = f.sel(time=slice(start_time,end_time)) # select only deployment dates provided
    fN = f_slice.source
    
    global fName
    head, tail = os.path.split(url)
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


