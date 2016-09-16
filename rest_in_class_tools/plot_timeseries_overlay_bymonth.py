#! /usr/local/bin/python

"""
Created on Wed Aug 24 2016

@author: lgarzio
"""

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.lines as mlines
import plotting.plot_functions as pf
import numpy as np
import os
import re
import datetime
import pandas as pd

'''
This script is used to create timeseries plots of telemetered and recovered data from netCDF or ncml files, by month,
between a time range specified by the user (must be < 1 year).
"Overlay" plots plot telemetered and recovered data on top of each other by month, and provide min and max values.
"Panel" plots create 3 plots on one page
    1. The top plot is a re-created overlay plot, by month
    2. The middle plot is recovered data only, by month
    3. The bottom plot is telemetered data only, by month
'''

recovered = 'http://opendap.oceanobservatories.org/thredds/dodsC/rest-in-class/Coastal_Endurance/CE05MOAS/05-CTDGVM000/recovered_host/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml'
telemetered = 'http://opendap.oceanobservatories.org/thredds/dodsC/rest-in-class/Coastal_Endurance/CE05MOAS/05-CTDGVM000/telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml'
save_dir = '/Users/lgarzio/Documents/OOI/DataReviews/restinclass/Endurance'

# enter deployment dates
start_time = datetime.datetime(2014, 04, 01, 0, 0, 0)
end_time = datetime.datetime(2014, 05, 29, 0, 0, 0)

rec = xr.open_dataset(recovered)
tel = xr.open_dataset(telemetered)

rec = rec.swap_dims({'obs':'time'})
tel = tel.swap_dims({'obs':'time'})

# Select only the time range indicated
rec_slice = rec.sel(time=slice(start_time,end_time))
tel_slice = tel.sel(time=slice(start_time,end_time))

global fName
head, tail = os.path.split(recovered)
fName = tail.split('.', 1)[0]
title = fName[0:27]
platform1 = title.split('-')[0]
platform2 = platform1 + '-' + title.split('-')[1]


# Identifies variables to skip when plotting
misc_vars = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc', 'time', 'mission', 'obs']
reg_ex = re.compile('|'.join(misc_vars))

sci_vars_rec = [s for s in rec.variables if not reg_ex.search(s)]
sci_vars_tel = [s for s in tel.variables if not reg_ex.search(s)]


# Index time by month (recovered and telemetered)
time_rec = rec_slice['time']
gMonth_rec = time_rec['time.month']
months_rec = np.unique(gMonth_rec.data)

time_tel = tel_slice['time']
gMonth_tel = time_tel['time.month']
months_tel = np.unique(gMonth_tel.data)

print 'Recovered months present in file: ' + str(months_rec)
print 'Telemetered months present in file: ' + str(months_tel)

# Only plots months contained in the recovered dataset, if there is additional telemetered data it won't be plotted
for x in months_rec:
    ind_month_rec = x == gMonth_rec.data
    temp_time_rec = time_rec.data[ind_month_rec]

    ind_month_tel = x == gMonth_tel.data
    temp_time_tel = time_tel.data[ind_month_tel]

    for r in sci_vars_rec:
        for t in sci_vars_tel:
            if r == t: # check if r and t are the same variable

                r_var = rec_slice.variables[r]
                r_data = rec_slice.variables[r].data[ind_month_rec]

                t_var = tel_slice.variables[t]
                t_data = tel_slice.variables[t].data[ind_month_tel]

                try:
                    y_units = rec_slice[r].units
                except AttributeError:
                    continue

                # get min and max for recovered data
                try:
                    r_min = np.nanmin(r_data)
                except TypeError:
                    continue

                try:
                    r_max = np.nanmax(r_data)
                except TypeError:
                    continue

                # get min and max for telemetered data
                try:
                    t_min = np.nanmin(t_data)
                except TypeError:
                    continue

                try:
                    t_max = np.nanmax(t_data)
                except TypeError:
                    continue

                # set up overlay plot
                fig, ax = plt.subplots()
                plt.grid()
                plt.margins(y=.1, x=.1)

                # create plot of recovered data
                try:
                    ax.plot(temp_time_rec, r_data, 'o', markerfacecolor='none', markeredgecolor='r', lw=.75)
                except ValueError:
                    print 'x and y must be the same size'
                    continue

                # overlay plot of telemetered data
                try:
                    ax.plot(temp_time_tel, t_data, 'x', markeredgecolor='b', lw=1.5)
                except ValueError:
                    print 'x and y must be the same size'
                    continue

                # Format date axis
                df = mdates.DateFormatter('%Y-%m-%d')
                ax.xaxis.set_major_formatter(df)
                fig.autofmt_xdate()

                # Format y-axis to disable offset
                y_formatter = ticker.ScalarFormatter(useOffset=False)
                ax.yaxis.set_major_formatter(y_formatter)

                # Labels
                ax.set_ylabel(rec[r].name + " ("+ y_units + ")")
                m = datetime.date(1900, x, 1).strftime('%B')
                year = str(pd.Timestamp(temp_time_rec[0]).year)
                ax.set_title(title + '_' + m + year, fontsize=10)

                # Format legend
                rec_leg = mlines.Line2D([], [], markerfacecolor='none', marker='o', markeredgecolor='r', color='r',
                                        label=("Recovered" + "\n  Max: %f" % r_max + "\n  Min: %f" % r_min))
                rec_tel = mlines.Line2D([], [], marker='x', markeredgecolor='b', ls=':',
                                        label=("Telemetered" + "\n  Max: %f" % t_max + "\n  Min: %f" % t_min))
                ax.legend(handles=[rec_leg, rec_tel],loc='best', fontsize=8)

                # Save plot
                filename = title + "_" + r + "_" + str(x) + "-" + year + "_overlay"
                dir1 = os.path.join(save_dir, platform1, platform2, title, "overlay_plots_bymonth")
                pf.create_dir(dir1)
                save_file = os.path.join(dir1, filename)  # create save file name
                plt.savefig(str(save_file),dpi=150) # save figure
                plt.close()



                #
                # # Set up panel plot
                # fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=True)
                # #plt.grid()
                # plt.margins(y=.1, x=.1)
                #
                # # plot recovered data
                # try:
                #     ax1.plot(temp_time_rec, r_data, 'o', markerfacecolor='none', markeredgecolor='r', lw=.75, label='recovered')
                #     ax1.xaxis.grid(True)
                #     ax1.yaxis.grid(True)
                # except ValueError:
                #     print 'x and y must be the same size'
                #     continue
                #
                # try:
                #     ax2.plot(temp_time_rec, r_data, 'o', markerfacecolor='none', markeredgecolor='r', lw=.75, label='recovered')
                #     ax2.xaxis.grid(True)
                #     ax2.yaxis.grid(True)
                # except ValueError:
                #     print 'x and y must be the same size'
                #     continue
                #
                # #plot telemetered data
                # try:
                #     ax1.plot(temp_time_tel, t_data, 'x', markeredgecolor='b', lw=1.5, label='telemetered')
                # except ValueError:
                #     print 'x and y must be the same size'
                #     continue
                #
                # try:
                #     ax3.plot(temp_time_tel, t_data, 'x', markeredgecolor='b', lw=1.5, label='telemetered')
                #     ax3.xaxis.grid(True)
                #     ax3.yaxis.grid(True)
                # except ValueError:
                #     print 'x and y must be the same size'
                #     continue
                #
                # # Format date axis
                # df = mdates.DateFormatter('%Y-%m-%d')
                # ax1.xaxis.set_major_formatter(df)
                # fig.autofmt_xdate()
                #
                # # Format y-axis to disable offset
                # y_formatter = ticker.ScalarFormatter(useOffset=False)
                # ax1.yaxis.set_major_formatter(y_formatter)
                #
                # # Labels
                # ax2.set_ylabel(rec[r].name + " ("+ y_units + ")")
                # ax1.set_title(title + '_' + m + year, fontsize=10)
                #
                # # Legends
                # ax1.legend(loc='best', fontsize=6, markerscale=.5)
                # ax2.legend(loc='best', fontsize=6, markerscale=.5)
                # ax3.legend(loc='best', fontsize=6, markerscale=.5)
                #
                # # Save plot
                # filename = title + "_" + r + "_" + str(x) + "-" + year + "_panel"
                # dir2 = os.path.join(save_dir,  platform1, platform2, title, "panel_plots_bymonth")
                # pf.create_dir(dir2)
                # save_file = os.path.join(dir2, filename)  # create save file name
                # plt.savefig(str(save_file),dpi=150) # save figure
                # plt.close()