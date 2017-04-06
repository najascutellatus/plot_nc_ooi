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


def main(nc, directory, out, time_break, breakdown):
    """
    files: url to an .nc/.ncml file or the path to a text file containing .nc/.ncml links. A # at the front will skip links in the text file.
    out: Directory to save plots
    """
    list_files = directory + "/*.nc"
    # list_files = ['https://opendap.oceanobservatories.org/thredds/dodsC/ooi/friedrich-knuth-gmail/20170322T191659-RS03AXPS-PC03A-4A-CTDPFA303-streamed-ctdpf_optode_sample/deployment0003_RS03AXPS-PC03A-4A-CTDPFA303-streamed-ctdpf_optode_sample_20170312T000000.426102-20170322T190000.059973.nc',
    # 'https://opendap.oceanobservatories.org/thredds/dodsC/ooi/friedrich-knuth-gmail/20170322T191659-RS03AXPS-PC03A-4A-CTDPFA303-streamed-ctdpf_optode_sample/deployment0003_RS03AXPS-PC03A-4A-CTDPFA303-streamed-ctdpf_optode_sample_20161222T000000.132709-20170311T235959.426096.nc']
    # print list_files
    stream_vars = pf.load_variable_dict(var='eng')  # load engineering variables

    with xr.open_dataset(nc, mask_and_scale=False) as ds_ncfile:
        stream = ds_ncfile.stream  # List stream name associated with the data
        title_pre = mk_str(ds_ncfile.attrs, 't')  # , var, tt0, tt1, 't')
        save_pre = mk_str(ds_ncfile.attrs, 's')  # , var, tt0, tt1, 's')
        platform = ds_ncfile.subsite
        node = ds_ncfile.node
        sensor = ds_ncfile.sensor
        # save_dir = os.path.join(out, platform, node, stream, 'xsection_depth_profiles')
        save_dir = os.path.join(out,'timeseries',breakdown)
        cf.create_dir(save_dir)


    with xr.open_mfdataset(list_files) as ds:
        # change dimensions from 'obs' to 'time'
        ds = ds.swap_dims({'obs': 'time'})
        ds_variables = ds.data_vars.keys()  # List of dataset variables

        # try:
        #     eng = stream_vars[stream]  # select specific streams engineering variables
        # except KeyError:
        #     eng = ['']

        misc = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc',  'time', 'mission', 'obs',
        'volt', 'ref', 'sig', 'amp', 'rph', 'calphase', 'phase', 'therm']

        # reg_ex = re.compile('|'.join(eng+misc))  # make regular expression
        reg_ex = re.compile('|'.join(misc))

        #  keep variables that are not in the regular expression
        sci_vars = [s for s in ds_variables if not reg_ex.search(s)]

        # t0, t1 = pf.get_rounded_start_and_end_times(ds_disk['time'].data)
        # tI = (pd.to_datetime(t0) + (pd.to_datetime(t1) - pd.to_datetime(t0)) / 2)
        # time_list = [[t0, t1], [t0, tI], [tI, t1]]

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

                try:
                    y_lab = sci.long_name
                except AttributeError:
                    y_lab = sci.standard_name
                y = dict(data=sci.data[time_ind], info=dict(label=y_lab, units=str(sci.units), var=var,
                                                            platform=platform, node=node, sensor=sensor))

                title = title_pre + var

                # plot timeseries with outliers
                fig, ax = pf.auto_plot(x, y, title, stdev=None, line_style='.', g_range=True)
                pf.resize(width=12, height=8.5)  # Resize figure

                save_name = '{}-{}-{}_{}_{}-{}'.format(platform, node, sensor, var, t0, t1)
                pf.save_fig(save_dir, save_name, res=150)  # Save figure
                plt.close('all')
                # try:
                #     y_lab = sci.standard_name
                # except AttributeError:
                #     y_lab = var
                # y = dict(data=sci.data, info=dict(label=y_lab, units=sci.units))

                # plot timeseries with outliers removed
                # fig, ax = pf.auto_plot(x, y, title, stdev=1, line_style='.', g_range=True)
                # pf.resize(width=12, height=8.5)  # Resize figure

                # save_name = '{}-{}-{}_{}_{}-{}_outliers_removed'.format(platform, node, sensor, var, t0, t1)
                # pf.save_fig(save_dir, save_name, res=150)  # Save figure
                # plt.close('all')
            del x, y
if __name__ == '__main__':
    nc_file = '/Users/knuth/Downloads/d2/deployment0002_CE04OSBP-LJ01C-06-CTDBPO108-streamed-ctdbp_no_sample_20150803T231918.079541-20150916T235959.611749.nc'
    times = 'time.year'
    breakdown = 'by_year'
    files_location = '/Users/knuth/Downloads/d2'
    output_dir = '/Users/knuth/Downloads/d2'
    main(nc_file, files_location, output_dir, times, breakdown)

