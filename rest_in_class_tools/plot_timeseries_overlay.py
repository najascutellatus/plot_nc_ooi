#! /usr/local/bin/python

"""
Created on Mon Aug 22 2016

@author: lgarzio
"""

import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.lines as mlines
import numpy as np
import os
import re

'''
This script is used to create timeseries plots of telemetered and recovered data from netCDF or ncml files.
"Overlay" plots plot telemetered and recovered data on top of each other, and provide min and max values.
"Panel" plots create 3 plots on one page
    1. The top plot is a re-created overlay plot
    2. The middle plot is recovered data only
    3. The bottom plot is telemetered data only
'''

recovered = 'http://opendap.oceanobservatories.org/thredds/dodsC/rest-in-class/Coastal_Endurance/CE05MOAS/05-CTDGVM000/recovered_host/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml'
telemetered = 'http://opendap.oceanobservatories.org/thredds/dodsC/rest-in-class/Coastal_Endurance/CE05MOAS/05-CTDGVM000/telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml'
save_dir = '/Users/lgarzio/Documents/OOI/DataReviews/restinclass/Endurance'

rec = nc.Dataset(recovered)
tel = nc.Dataset(telemetered)

global fName
head, tail = os.path.split(recovered)
fName = tail.split('.', 1)[0]
title = fName[0:27]
platform1 = title.split('-')[0]
platform2 = platform1 + '-' + title.split('-')[1]

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

# Gets the recovered and telemetered time variables and converts to dates
time_rec_var = rec.variables['time']
time_rec_num = time_rec_var[:]
time_rec_num_units = time_rec_var.units
time_rec = nc.num2date(time_rec_num, time_rec_num_units)

time_tel_var = tel.variables['time']
time_tel_num = time_tel_var[:]
time_tel_num_units = time_tel_var.units
time_tel = nc.num2date(time_tel_num, time_tel_num_units)

# Identifies variables to skip when plotting
misc_vars = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc', 'time', 'mission', 'obs']
reg_ex = re.compile('|'.join(misc_vars))

sci_vars_rec = [s for s in rec.variables if not reg_ex.search(s)]
sci_vars_tel = [s for s in tel.variables if not reg_ex.search(s)]

for r in sci_vars_rec:
    for t in sci_vars_tel:
        if r == t: # check if r and t are the same variable

            r_var = rec.variables[r]
            r_data = r_var[:]

            t_var = tel.variables[t]
            t_data = t_var[:]

            try:
                y_units = r_var.units
            except AttributeError:
                y_units = ""
                continue

            # get min and max for recovered data
            try:
                r_min = np.nanmin(r_data)
            except TypeError:
                r_min = ""
                continue

            try:
                r_max = np.nanmax(r_data)
            except TypeError:
                r_max = ""
                continue

            # get min and max for telemetered data
            try:
                t_min = np.nanmin(t_data)
            except TypeError:
                t_min = ""
                continue

            try:
                t_max = np.nanmax(t_data)
            except TypeError:
                t_max = ""
                continue

            # set up overlay plot
            fig, ax = plt.subplots()
            plt.grid()
            plt.margins(y=.1, x=.1)

            # create plot of recovered data
            try:
                #rec_plot = plt.plot(time_rec, r_data, 'o', markerfacecolor='none', markeredgecolor='r', lw=.75, ls='-', color='r')
                ax.plot(time_rec, r_data, 'o', markerfacecolor='none', markeredgecolor='r', lw=.75)
            except ValueError:
                print 'x and y must be the same size'
                continue

            # overlay plot of telemetered data
            try:
                #tel_plot = plt.plot(time_tel, t_data, 'x', markeredgecolor='b', lw=1.5, ls=':', color='b')
                ax.plot(time_tel, t_data, 'x', markeredgecolor='b', lw=1.5)
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
            ax.set_title(title, fontsize=10)

            # Format legend
            rec_leg = mlines.Line2D([], [], markerfacecolor='none', marker='o', markeredgecolor='r', color='r',
                                    label=("Recovered" + "\n  Max: %f" % r_max + "\n  Min: %f" % r_min))
            rec_tel = mlines.Line2D([], [], marker='x', markeredgecolor='b', ls=':',
                                    label=("Telemetered" + "\n  Max: %f" % t_max + "\n  Min: %f" % t_min))
            ax.legend(handles=[rec_leg, rec_tel],loc='best', fontsize=8)

            # Save plot
            filename = title + "_" + r + "_overlay"
            dir1 = os.path.join(save_dir, platform1, platform2, title, "overlay_plots")
            createDir(dir1)
            save_file = os.path.join(dir1, filename)  # create save file name
            plt.savefig(str(save_file),dpi=150) # save figure
            plt.close()

            # Set up panel plot
            fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=True)
            #plt.grid()
            plt.margins(y=.1, x=.1)

            # plot recovered data
            try:
                ax1.plot(time_rec, r_data, 'o', markerfacecolor='none', markeredgecolor='r', lw=.75, label='recovered')
                ax1.xaxis.grid(True)
                ax1.yaxis.grid(True)
            except ValueError:
                print 'x and y must be the same size'
                continue

            try:
                ax2.plot(time_rec, r_data, 'o', markerfacecolor='none', markeredgecolor='r', lw=.75, label='recovered')
                ax2.xaxis.grid(True)
                ax2.yaxis.grid(True)
            except ValueError:
                print 'x and y must be the same size'
                continue

            #plot telemetered data
            try:
                ax1.plot(time_tel, t_data, 'x', markeredgecolor='b', lw=1.5, label='telemetered')
            except ValueError:
                print 'x and y must be the same size'
                continue

            try:
                ax3.plot(time_tel, t_data, 'x', markeredgecolor='b', lw=1.5, label='telemetered')
                ax3.xaxis.grid(True)
                ax3.yaxis.grid(True)
            except ValueError:
                print 'x and y must be the same size'
                continue

            # Format date axis
            df = mdates.DateFormatter('%Y-%m-%d')
            ax1.xaxis.set_major_formatter(df)
            fig.autofmt_xdate()

            # Format y-axis to disable offset
            y_formatter = ticker.ScalarFormatter(useOffset=False)
            ax1.yaxis.set_major_formatter(y_formatter)

            # Labels
            ax2.set_ylabel(rec[r].name + " ("+ y_units + ")")
            ax1.set_title(title, fontsize=10)

            # Legends
            ax1.legend(loc='best', fontsize=6, markerscale=.5)
            ax2.legend(loc='best', fontsize=6, markerscale=.5)
            ax3.legend(loc='best', fontsize=6, markerscale=.5)

            # Save plot
            filename = title + "_" + r + "_panel"
            dir2 = os.path.join(save_dir, platform1, platform2, title, "panel_plots")
            createDir(dir2)
            save_file = os.path.join(dir2, filename)  # create save file name
            plt.savefig(str(save_file),dpi=150) # save figure
            plt.close()