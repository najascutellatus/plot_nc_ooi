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
import os
import re
import pandas as pd
'''
This script is used to create timeseries plots of telemetered and recovered data from netCDF or ncml files ONLY where the
Long Names of the telemetered and recovered data products are the same
'''

recovered = 'https://opendap.oceanobservatories.org/thredds/dodsC/ooi/lgarzio-marine-rutgers/20170413T193714-GA01SUMO-RID16-03-CTDBPF000-recovered_inst-ctdbp_cdef_instrument_recovered/deployment0002_GA01SUMO-RID16-03-CTDBPF000-recovered_inst-ctdbp_cdef_instrument_recovered_20151114T210604-20161108T100953.nc'
telemetered = 'https://opendap.oceanobservatories.org/thredds/dodsC/ooi/lgarzio-marine-rutgers/20170413T193707-GA01SUMO-RID16-03-CTDBPF000-telemetered-ctdbp_cdef_dcl_instrument/deployment0002_GA01SUMO-RID16-03-CTDBPF000-telemetered-ctdbp_cdef_dcl_instrument_20151114T210608.612000-20161108T000811.767000.nc'
out = '/Users/lgarzio/Documents/OOI/DataReviews/RIC/'


rec = xr.open_dataset(recovered)
tel = xr.open_dataset(telemetered)

platform = rec.subsite
node = rec.node
sensor = rec.sensor
rec_method = rec.collection_method

rec = rec.swap_dims({'obs':'time'})
tel = tel.swap_dims({'obs':'time'})

save_dir = os.path.join(out, rec.subsite, rec.node, rec.stream, 'timeseries_overlay_' + rec_method)
cf.create_dir(save_dir)

head, tail = os.path.split(recovered)
file_name = tail.split('.', 1)[0]
deployment = file_name[0:14]
title = deployment + '_' + platform + '-' + node + '-' + sensor

# Identifies variables to skip when plotting
misc_vars = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc', 'time', 'mission', 'obs']
reg_ex = re.compile('|'.join(misc_vars))

sci_vars_rec = [s for s in rec.variables if not reg_ex.search(s)]
sci_vars_tel = [s for s in tel.variables if not reg_ex.search(s)]

# find where the Long Names of the variables are the same (because the parameter names aren't always the same)
rec_name = []
rec_long_name = []
for rvars in sci_vars_rec:
    rec_name.append(rvars)  # list of recovered variable names

    try:
        rv_longname = rec[rvars].long_name
    except AttributeError:
        rv_longname = rvars

    rec_long_name.append(rv_longname)  # list of recovered long names

rec_df = pd.DataFrame({'rec_name': rec_name, 'long_name': rec_long_name})

tel_name = []
tel_long_name = []
for tvars in sci_vars_tel:
    tel_name.append(tvars)  # list of telemetered variable names

    try:
        tv_longname = tel[tvars].long_name
    except AttributeError:
        tv_longname = tvars

    tel_long_name.append(tv_longname)  # list of telemetered long names

tel_df = pd.DataFrame({'tel_name': tel_name, 'long_name': tel_long_name})

mapping = pd.merge(rec_df, tel_df, on='long_name',how='inner')  # map the recovered and telemetered names based on long name

for row in mapping.itertuples():
    index,long_name,rec_name,tel_name = row
    r_var = rec[rec_name]
    r_data = r_var.data

    t_var = tel[tel_name]
    t_data = t_var.data

    time_rec = rec['time'].data
    time_tel = tel['time'].data

    x1 = dict(data=time_rec, info=dict(platform=platform, node=node, sensor=sensor,  units='GMT', label='Time', var=rec_name))
    y1 = dict(data=r_data, info=dict(platform=platform, node=node, sensor=sensor, label=long_name, units=r_var.units, var=rec_name))

    x2 = dict(data=time_tel, info=dict(platform=platform, node=node, sensor=sensor,  units='GMT', label='Time', var=tel_name))
    y2 = dict(data=t_data, info=dict(platform=platform, node=node, sensor=sensor, label=long_name, units=t_var.units, var=tel_name))

    fig,ax = pf.compare_timeseries(x1, y1, x2, y2, g_range=True)

    title_text = '{}\nVariable: {}\ntelemetered ({}) vs {} ({})'.format(title, long_name, tel_name, rec_method, rec_name)
    plt.title(title_text, fontsize=10)
    pf.resize(width=12, height=8.5)  # Resize figure
    save_name = '{}_{}'.format(title, long_name)
    pf.save_fig(save_dir, save_name, res=150)  # Save figure
    plt.close('all')