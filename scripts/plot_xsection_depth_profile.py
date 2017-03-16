#! /usr/bin/env python
import os
import xarray as xr
import pandas as pd
import functions.plotting as pf
import functions.common as cf
import matplotlib.pyplot as plt
import re
import numpy as np
import calendar

fmt = '%Y.%m.%dT%H.%M.00'

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


def read_file(fname):
    file_list = []
    with open(fname) as f:
        for line in f:
            if line.find('#') is -1:
                file_list.append(line.rstrip('\n'))
            else:
                continue
    return file_list


def main(files, out, time_break, depth, start, end, interactive):
    """
    files: url to an .nc/.ncml file or the path to a text file containing .nc/.ncml links. A # at the front will skip links in the text file.
    out: Directory to save plots
    """
    fname, ext = os.path.splitext(files)
    if ext in '.nc':
        list_files = [files]
    elif ext in '.ncml':
        list_files = [files]
    else:
        list_files = read_file(files)

    stream_vars = pf.load_variable_dict(var='eng')  # load engineering variables
    for nc in list_files:
        print nc
        with xr.open_dataset(nc, mask_and_scale=False) as ds:
            # change dimensions from 'obs' to 'time'
            ds = ds.swap_dims({'obs': 'time'})
            ds_variables = ds.data_vars.keys()  # List of dataset variables
            stream = ds.stream  # List stream name associated with the data
            title_pre = mk_str(ds.attrs, 't')  # , var, tt0, tt1, 't')
            save_pre = mk_str(ds.attrs, 's')  # , var, tt0, tt1, 's')
            platform = ds.subsite
            node = ds.node
            sensor = ds.sensor
            save_dir = os.path.join(out,'xsection_depth_profiles')
            # save_dir = os.path.join(out, ds.subsite, ds.node, ds.stream, 'xsection_depth_profiles')
            cf.create_dir(save_dir)

            # try:
            #     eng = stream_vars[stream]  # select specific streams engineering variables
            # except KeyError:
            #     eng = ['']

            misc = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc',  'time', 'mission', 'obs',
            'volt', 'ref', 'sig', 'amp', 'rph', 'calphase', 'phase', 'therm', 'light']

            # reg_ex = re.compile('|'.join(eng+misc))  # make regular expression
            reg_ex = re.compile('|'.join(misc))

            #  keep variables that are not in the regular expression
            sci_vars = [s for s in ds_variables if not reg_ex.search(s)]

            # t0, t1 = pf.get_rounded_start_and_end_times(ds_disk['time'].data)
            # tI = (pd.to_datetime(t0) + (pd.to_datetime(t1) - pd.to_datetime(t0)) / 2)
            # time_list = [[t0, t1], [t0, tI], [tI, t1]]

            if not time_break == None:
                times = np.unique(ds[time_break])
            
                for t in times:
                    time_ind = t == ds[time_break].data
                    for var in sci_vars:
                        x = dict(data=ds['time'].data[time_ind],
                                 info=dict(label='Time', units='GMT'))
                        t0 = pd.to_datetime(x['data'].min()).strftime('%Y-%m-%dT%H%M%00')
                        t1 = pd.to_datetime(x['data'].max()).strftime('%Y-%m-%dT%H%M%00')
                        try:
                            sci = ds[var]
                            print var
                            # sci = sub_ds[var]
                        except UnicodeEncodeError: # some comments have latex characters
                            ds[var].attrs.pop('comment')  # remove from the attributes
                            sci = ds[var]  # or else the variable won't load


                        y = dict(data=ds[depth].data[time_ind], info=dict(label='Pressure', units='dbar', var=var,
                                                                    platform=platform, node=node, sensor=sensor))

                        
                        try:
                            z_lab = sci.long_name
                        except AttributeError:
                            z_lab = sci.standard_name
                        z = dict(data=sci.data[time_ind], info=dict(label=z_lab, units=sci.units, var=var,
                                                                    platform=platform, node=node, sensor=sensor))

                        title = title_pre + var

                        # plot timeseries with outliers
                        fig, ax = pf.depth_cross_section(x, y, z, title=title)
                        pf.resize(width=12, height=8.5)  # Resize figure

                        save_name = '{}-{}-{}_{}_{}-{}'.format(platform, node, sensor, var, t0, t1)
                        pf.save_fig(save_dir, save_name, res=150)  # Save figure
                        plt.close('all')
                        # try:
                        #     y_lab = sci.standard_name
                        # except AttributeError:
                        #     y_lab = var
                        # y = dict(data=sci.data, info=dict(label=y_lab, units=sci.units))

                    # del x, y

            else:
                ds = ds.sel(time=slice(start, end))

                for var in sci_vars:
                    x = dict(data=ds['time'].data[:],
                             info=dict(label='Time', units='GMT'))
                    t0 = pd.to_datetime(x['data'].min()).strftime('%Y-%m-%dT%H%M%00')
                    t1 = pd.to_datetime(x['data'].max()).strftime('%Y-%m-%dT%H%M%00')
                    try:
                        sci = ds[var]
                        print var
                        # sci = sub_ds[var]
                    except UnicodeEncodeError: # some comments have latex characters
                        ds[var].attrs.pop('comment')  # remove from the attributes
                        sci = ds[var]  # or else the variable won't load


                    y = dict(data=ds[depth].data[:], info=dict(label='Pressure', units='dbar', var=var,
                                                                platform=platform, node=node, sensor=sensor))


                    try:
                        z_lab = sci.long_name
                    except AttributeError:
                        z_lab = sci.standard_name
                    z = dict(data=sci.data[:], info=dict(label=z_lab, units=sci.units, var=var,
                                                                platform=platform, node=node, sensor=sensor))

                    title = title_pre + var

                    # plot timeseries with outliers
                    fig, ax = pf.depth_cross_section(x, y, z, title=title, interactive=interactive)

                    if interactive == True:
                        fig.canvas.mpl_connect('pick_event', lambda event: pf.onpick3(event, x['data'], y['data'], z['data']))
                        plt.show()

                    else:
                        pf.resize(width=12, height=8.5)  # Resize figure
                        save_name = '{}-{}-{}_{}_{}-{}'.format(platform, node, sensor, var, t0, t1)
                        pf.save_fig(save_dir, save_name, res=150)  # Save figure
                        plt.close('all')
                    # try:
                    #     y_lab = sci.standard_name
                    # except AttributeError:
                    #     y_lab = var
                    # y = dict(data=sci.data, info=dict(label=y_lab, units=sci.units))

                # del x, y

if __name__ == '__main__':
    nc_file = '/Users/knuth/Desktop/PCO2WA301/deployment3/deployment0003_RS03AXPS-SF03A-4F-PCO2WA301-streamed-pco2w_a_sami_data_record_20160714T220510.338788-20161201T064210.693177.nc'
    output_location = '/Users/knuth/Desktop/PCO2WA301/deployment3/plots_year_test'
    depth = 'ctdpf_sbe43_sample-seawater_pressure'
    times = None # example: 'time.month' Must be None to set interval between start_time and end_time
    start_time = '2016-09-13'
    end_time = '2016-09-17'
    interactive = True # set to True to create interactive plots, instead of saving plots to file.
    main(nc_file, output_location, times, depth, start_time, end_time, interactive)

