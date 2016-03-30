#! /usr/bin/env python
import os
import xarray as xr
import pandas as pd
import plotting.plot_functions as pf
import matplotlib.pyplot as plt
import re
import click as click
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
        string = site + '-' + node + ' Stream: ' + stream + '\n' + 'Variable: '
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


@click.command()
@click.argument('files', nargs=1, type=click.Path())
@click.argument('out', nargs=1, type=click.Path(exists=False))
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
        with xr.open_dataset(nc) as ds_disk:
            # change dimensions from 'obs' to 'time'
            ds_disk = ds_disk.swap_dims({'obs': 'time'})
            ds_variables = ds_disk.data_vars.keys()  # List of dataset variables
            stream = ds_disk.stream  # List stream name associated with the data
            title_pre = mk_str(ds_disk.attrs, 't')  # , var, tt0, tt1, 't')
            save_pre = mk_str(ds_disk.attrs, 's')  # , var, tt0, tt1, 's')
            save_dir = os.path.join(out, ds_disk.subsite, ds_disk.node, ds_disk.stream)
            pf.create_dir(save_dir)
            try:
                eng = stream_vars[stream]  # select specific streams engineering variables
            except KeyError:
                eng = ['']

            misc = ['timestamp', 'provenance', 'qc', 'id', 'obs', 'deployment',
                    'volts', 'counts']

            reg_ex = re.compile('|'.join(eng + misc))  # make regular expression

            #  keep variables that are not in the regular expression
            sci_vars = [s for s in ds_variables if not reg_ex.search(s)]

            if ds_disk.subsite[-4:] is not 'MOAS': # don't plot lat/lon for moorings
                reg_ll = re.compile('|'.join(['lon', 'lat']))
                sci_vars = [s for s in sci_vars if not reg_ll.search(s)]

            t0, t1 = pf.get_rounded_start_and_end_times(ds_disk['time'].data)
            tI = (pd.to_datetime(t0) + (pd.to_datetime(t1) - pd.to_datetime(t0)) / 2)
            time_list = [[t0, t1], [t0, tI], [tI, t1]]

            for period in time_list:
                tt0 = period[0]
                tt1 = period[1]
                sub_ds = ds_disk.sel(time=slice(str(tt0), str(tt1)))

                for var in sci_vars:
                    try:
                        # print var
                        sci = sub_ds[var]
                    except UnicodeEncodeError: # some comments have latex characters
                        sub_ds[var].attrs.pop('comment')  # remove from the attributes
                        sci = sub_ds[var]  # or else the variable won't load

                    x = dict(data=sub_ds['time'].data, info=dict(label=sub_ds['time'].standard_name, units='GMT'))
                    try:
                        y_lab = sci.long_name
                    except AttributeError:
                        y_lab = sci.standard_name
                    y = dict(data=sci.data, info=dict(label=y_lab, units=sci.units))

                    sname = save_pre + var + '-' + tt0.strftime(fmt) + '-' + tt1.strftime(fmt)
                    title = title_pre + var + '\n' + tt0.strftime(fmt) + ' - ' + tt1.strftime(fmt)
                    fig, ax = pf.auto_plot(x, y, title, stdev=3, line_style='r-o')
                    pf.resize(width=12, height=8.5)  # Resize figure
                    pf.save_fig(save_dir, sname, res=150)  # Save figure
                    plt.close('all')
                    del x, y
                del sub_ds

if __name__ == '__main__':
    # main('/Users/michaesm/Documents/dev/repos/ooi-data-review/plot-nc-ooi/thredds-links/2016.03.28T11.03.00-nc-links.txt', '/Users/michaesm/Documents/')
    main()
