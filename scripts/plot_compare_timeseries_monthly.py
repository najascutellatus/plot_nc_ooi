#! /usr/local/bin/python

"""
Created on Wed Aug 24 2016

@author: lgarzio
@modified: michaesm on September 16, 2016
"""

import xarray as xr
import matplotlib.pyplot as plt
import functions.plotting as pf
import functions.common as cf
from functions.common import compare_lists
import numpy as np
import os
import re
import datetime
import pandas as pd
import calendar
'''
This script is used to create timeseries plots of telemetered and recovered data from netCDF or ncml files, by month,
between a time range specified by the user (must be < 1 year).
'''

recovered = 'http://opendap.oceanobservatories.org/thredds/dodsC/rest-in-class/Coastal_Endurance/CE05MOAS/05-CTDGVM000/recovered_host/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml'
telemetered = 'http://opendap.oceanobservatories.org/thredds/dodsC/rest-in-class/Coastal_Endurance/CE05MOAS/05-CTDGVM000/telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CE05MOAS-GL319-05-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml'
out = '/Users/michaesm/Documents/'


rec = xr.open_dataset(recovered)
tel = xr.open_dataset(telemetered)

platform = rec.subsite
node = rec.node
sensor = rec.sensor

# deployments = pd.read_csv('/Users/michaesm/documents/dev/repos/ooi-data-review/plot-nc-ooi/tools/deployments_2016September.csv')
# temp = deployments[deployments['Reference Designator'].str.contains(platform)]

# enter deployment dates
# start_time = datetime.datetime(2014, 4, 1, 0, 0, 0)
# end_time = datetime.datetime(2014, 8, 29, 0, 0, 0)

rec = rec.swap_dims({'obs':'time'})
tel = tel.swap_dims({'obs':'time'})

save_dir = os.path.join(out, rec.subsite, rec.node, rec.stream, 'timeseries_overlay')
cf.create_dir(save_dir)

# Select only the time range indicated
# rec_slice = rec.sel(time=slice(start_time,end_time))
# tel_slice = tel.sel(time=slice(start_time,end_time))

head, tail = os.path.split(recovered)
file_name = tail.split('.', 1)[0]
title = file_name[0:27]
platform1 = title.split('-')[0]
platform2 = platform1 + '-' + title.split('-')[1]

# Identifies variables to skip when plotting
misc_vars = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc', 'time', 'mission', 'obs']
reg_ex = re.compile('|'.join(misc_vars))

sci_vars_rec = [s for s in rec.variables if not reg_ex.search(s)]
sci_vars_tel = [s for s in tel.variables if not reg_ex.search(s)]

[matching_vars, unmatched_rec] = compare_lists(sci_vars_rec, sci_vars_tel)
[_, unmatched_tel] = compare_lists(sci_vars_rec, sci_vars_tel)

print 'Variables present in both files: ' + str(matching_vars)
print 'Variables present in recovered but not telemetered: ' + str(unmatched_rec)
print 'Variables present in telemetered but not recovered: ' + str(unmatched_tel)

# Index time by month (recovered and telemetered)
months_rec = np.unique(rec['time.month'])
print 'Recovered months present in file: ' + str(months_rec)

# Only plots months contained in the recovered dataset, if there is additional telemetered data it won't be plotted
for month in months_rec:
    ind_month_rec = month == rec['time.month'].data # get index of this month for the recovered dataset
    ind_month_tel = month == tel['time.month'].data # get index of this month for the telemetered dataset

    temp_time_rec = rec['time'].data[ind_month_rec]
    temp_time_tel = tel['time'].data[ind_month_tel]

    for var in matching_vars:
        r_var = rec[var]
        r_data = r_var.data[ind_month_rec]

        t_var = tel[var]
        t_data = t_var.data[ind_month_tel]

        x1 = dict(data=temp_time_rec, info=dict(platform=platform, node=node, sensor=sensor,  units='GMT', label='Time', var=var))
        y1 = dict(data=r_data, info=dict(platform=platform, node=node, sensor=sensor, label=var, units=r_var.units, var=var))

        x2 = dict(data=temp_time_tel, info=dict(platform=platform, node=node, sensor=sensor,  units='GMT', label='Time', var=var))
        y2 = dict(data=t_data, info=dict(platform=platform, node=node, sensor=sensor, label=var, units=t_var.units, var=var))

        fig,ax = pf.compare_timeseries(x1, y1, x2, y2, g_range=True)

        title_text = '{}\nVariable: {}\nYear-Month: {}-{}'.format(title, var, pd.to_datetime(temp_time_rec[0]).year, calendar.month_name[month])
        plt.title(title_text)
        pf.resize(width=12, height=8.5)  # Resize figure
        save_name = '{}_{}_{}{}'.format(title, var, calendar.month_name[month], pd.to_datetime(temp_time_rec[0]).year)
        pf.save_fig(save_dir, save_name, res=150)  # Save figure
        plt.close('all')