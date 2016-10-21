#! /usr/bin/env python
import os
import xarray as xr
import pandas as pd
import functions.plotting as pf
import functions.common as cf
import matplotlib.pyplot as plt
import re
# import click as click

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
        string = site + '-' + node + ' Stream: ' + stream + ' '
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


# @click.command()
# @click.argument('files', nargs=1, type=click.Path())
# @click.argument('out', nargs=1, type=click.Path(exists=False))
def main(files, out):
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

        # the engine that xarray uses can be changed as specified here 
        # http://xarray.pydata.org/en/stable/generated/xarray.open_dataset.html#xarray.open_dataset

        with xr.open_dataset(nc, engine='netcdf4') as ds_disk:

            # change dimensions from 'obs' to 'time'
            ds_disk = ds_disk.swap_dims({'obs': 'time'})
            ds_variables = ds_disk.data_vars.keys()  # List of dataset variables
            stream = ds_disk.stream  # List stream name associated with the data
            title_pre = mk_str(ds_disk.attrs, 't')  # , var, tt0, tt1, 't')
            save_pre = mk_str(ds_disk.attrs, 's')  # , var, tt0, tt1, 's')
            save_dir = os.path.join(out, ds_disk.subsite, ds_disk.node, ds_disk.stream, 'pcolor')
            cf.create_dir(save_dir)

            t0, t1 = cf.get_rounded_start_and_end_times(ds_disk['time'].data)
            tI = (pd.to_datetime(t0) + (pd.to_datetime(t1) - pd.to_datetime(t0)) / 2)
            time_list = [[t0, t1], [t0, tI], [tI, t1]]
            # time_list = [[t0, t1]]

            for period in time_list:
                tt0 = period[0]
                tt1 = period[1]
                sub_ds = ds_disk.sel(time=slice(str(tt0), str(tt1)))
                bins = sub_ds['bin_depths']
                north = sub_ds['northward_seawater_velocity']
                east = sub_ds['eastward_seawater_velocity']
                # up = sub_ds['upward_seawater_velocity']
                # error = sub_ds['error_velocity']

                time = dict(data=pd.to_datetime(sub_ds['time'].data), info=dict(label=sub_ds['time'].standard_name, units='GMT'))
                bins = dict(data=bins.data.T, info=dict(label=bins.long_name, units=bins.units))
                north = dict(data=north.data.T, info=dict(label=north.long_name, units=north.units))
                east = dict(data=east.data.T, info=dict(label=east.long_name, units=east.units))
                # up = dict(data=up.data.T, info=dict(label=up.long_name, units=up.units))
                # error = dict(data=error.data.T, info=dict(label=error.long_name, units=error.units))

                sname = save_pre + 'ADCP-' + tt0.strftime(fmt) + '-' + tt1.strftime(fmt)
                title = title_pre + tt0.strftime(fmt) + ' - ' + tt1.strftime(fmt)
                fig, axs = pf.adcp(time, bins, north, east, title)
                pf.resize(width=12, height=8.5)  # Resize figure
                pf.save_fig(save_dir, sname, res=250)  # Save figure
                plt.close('all')
                # del sub_ds, x, y


if __name__ == '__main__':
    # main("http://opendap.oceanobservatories.org:8090/thredds/dodsC/ooi/friedrich-knuth-gmail/20161007T055559-RS01SBPS-PC01A-05-ADCPTD102-streamed-adcp_velocity_beam/deployment0000_RS01SBPS-PC01A-05-ADCPTD102-streamed-adcp_velocity_beam.ncml", ".")
    main("http://opendap.oceanobservatories.org:8090/thredds/dodsC/ooi/friedrich-knuth-gmail/20161019T085827-RS01SBPS-PC01A-05-ADCPTD102-streamed-adcp_velocity_beam/deployment0000_RS01SBPS-PC01A-05-ADCPTD102-streamed-adcp_velocity_beam.ncml", "/Users/knuth/Desktop/adcp/month/")