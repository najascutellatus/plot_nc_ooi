# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 12:46:22 2015

@author: michaesm
"""
import netCDF4 as nc
import matplotlib.pyplot as plt 
import matplotlib.dates as mDate
import matplotlib.ticker as ticker
import pytz

ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/spikr/spkir_data_record_L1.nc'
yVarName = 'spkir_downwelling_vector'
group = 'derived'

f = nc.Dataset(ncFile)

timeD = f.variables['time'][:]
timeU = f.variables['time'].units
timeD = nc.num2date(timeD, timeU)

if not group:
    y = f.groups[group]
else:
    y = f
    
y = y.variables[yVarName]
yU = y.units
yD = y[:]

xM = mDate.date2num(timeD)

fig,ax = plt.subplots()
minorLocator = ticker.AutoMinorLocator()
ax.plot_date(xM, yD, xdate=True, ydate=False,
             tz=pytz.utc, color='black', linestyle='-',
             linewidth=.5, marker='o', markersize=4,
             markerfacecolor='red', markeredgecolor='black')
             
fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 12
fig_size[1] = 8.5
plt.rcParams["figure.figsize"] = fig_size

# setup axes
#plt.ylim((yTuple[3], yTuple[4]))
ax.xaxis.set_minor_locator(minorLocator)
xax = ax.get_xaxis().get_major_formatter()

xax.scaled = {
    365.0 : '%Y-M', # data longer than a year
    30.   : '%Y-m\n%d', # set the > 1m < 1Y scale to Y-m
    1.0   : '%b-%d\n%H:%M', # set the > 1d < 1m scale to Y-m-d
    1./24.: '%b-%d\n%H:%M', # set the < 1d scale to H:M
    1./48.: '%b-%d\n%H:%M:%S',
    }
    
y_formatter = ticker.ScalarFormatter(useOffset=False)
ax.yaxis.set_major_formatter(y_formatter)
plt.grid()
    

#ax.set_title(fName) # title
ax.set_xlabel("Time (UTC)")
ax.set_ylabel(yVarName + "(" + yU + ")")

plt.show()