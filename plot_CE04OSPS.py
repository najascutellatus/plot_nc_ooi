#! /usr/local/bin/python

import sys, os, time, re
import netCDF4 as nc
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy as sp

def isfillvalue(a):
    """
    Test element-wise for fill values and return result as a boolean array.
    :param a: array_like
    :return: ndarray
    """
    a = np.asarray(a)
    if a.dtype.kind == 'i':
        mask = a == -999999999
    elif a.dtype.kind == 'f':
        mask = np.isnan(a)
    elif a.dtype.kind == 'S':
        mask = a == ''
    else:
        raise ValueError('Fill value not known for dtype %s' % (a.dtype))
    return mask

class StreamEngineException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class InvalidInterpolationException(StreamEngineException):
    """
    Internal error. Invalid interpolation was attempted.
    """
    status_code = 500

def interpolate_list(desired_time, data_time, data):
    if len(data) == 0:
        raise InvalidInterpolationException("Can't perform interpolation, data is empty".format(len(data_time), len(data)))

    if len(data_time) != len(data):
        raise InvalidInterpolationException("Can't perform interpolation, time len ({}) does not equal data len ({})".format(len(data_time), len(data)))

    try:
        float(data[0])  # check that data can be interpolated
    except (ValueError, TypeError):
        raise InvalidInterpolationException("Can't perform interpolation, type ({}) cannot be interpolated".format(type(data[0])))
    else:
        mask = np.logical_not(isfillvalue(data))
        data_time = np.asarray(data_time)[mask]
        data = np.asarray(data)[mask]
        if len(data) == 0:
            raise InvalidInterpolationException("Can't perform interpolation, data is empty".format(len(data_time), len(data)))
        return sp.interp(desired_time, data_time, data)

def plot_cross_section(x, y, z, args):
    # Close any existing plots
    plt.close('all')

    fig,ax = plt.subplots()
    plt.grid()
    # ax = plt.gca()
    ax.invert_yaxis()
    # f, ax = plt.subplots(1, 1)

    # Image size
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 8.5
    plt.rcParams["figure.figsize"] = fig_size

    # Format the date axis
    plt.locator_params(nbins=4)
    df = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(df)
    fig.autofmt_xdate()

    # colors = cm.rainbow(np.linspace(0,1, len(z)))
    # c = cm.jet(z)
    sc = plt.scatter(x, y, s=2, c=z, edgecolors='face')

    # add colorbar
    cb = fig.colorbar(sc, ax=ax, label=args[2] + " (" + args[3] + ")")
    cb.formatter.set_useOffset(False)
    # cb.ax.yaxis.set_offset_position('right')
    cb.update_ticks()

    # plot labels
    # ax.set_title(args)
    plt.ylabel(args[0] + ' (' + args[1] + ')') # y label
    plt.xlabel("Time (GMT)")

    plt.savefig(args[4], dpi=100) # save figure
    plt.close()

def reject_outliers(data, m=3):
    # function to reject outliers beyond 3 standard deviations of the mean.
    # data: numpy array containing data
    # m: the number of standard deviations from the mean. Default: 3
    return abs(data - np.mean(data)) < m * np.std(data)


url_ctd='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-3/Coastal_Endurance/CE04OSPS/2A-CTDPFA107/streamed/CE04OSPS-SF01B-2A-CTDPFA107-ctdpf_sbe43_sample-streamed/CE04OSPS-SF01B-2A-CTDPFA107-ctdpf_sbe43_sample-streamed.ncml'
url_flor='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-3/Coastal_Endurance/CE04OSPS/3A-FLORTD104/streamed/CE04OSPS-SF01B-3A-FLORTD104-flort_d_data_record-streamed/CE04OSPS-SF01B-3A-FLORTD104-flort_d_data_record-streamed.ncml'
url_nutnr='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-3/Coastal_Endurance/CE04OSPS/4A-NUTNRA102/streamed/CE04OSPS-SF01B-4A-NUTNRA102-nutnr_a_sample-streamed/CE04OSPS-SF01B-4A-NUTNRA102-nutnr_a_sample-streamed.ncml'

start_time = datetime.datetime(2015, 10, 18, 0, 0, 0)
end_time = datetime.datetime(2015, 10, 25, 0, 0, 0)

# load CTD dataset
ctd = nc.Dataset(url_ctd)

# convert nc time to datetime and find indices where time is between start and end times set above.
time_ctd = nc.num2date(ctd.variables['time'][:], ctd.variables['time'].units)
time_ind = np.where((time_ctd > start_time) & (time_ctd < end_time))
time_ctd = time_ctd[time_ind]
time_ctd_num = nc.date2num(time_ctd, 'seconds since 1970-01-01')

pressure = ctd.variables['seawater_pressure'][time_ind]; pressure_units = ctd.variables['seawater_pressure'].units

density = ctd.variables['seawater_density'][time_ind]; density_units = ctd.variables['seawater_density'].units
salinity = ctd.variables['practical_salinity'][time_ind]; salinity_units = ctd.variables['seawater_density'].units
temperature = ctd.variables['seawater_temperature'][time_ind]; temperature_units = ctd.variables['seawater_temperature'].units
conductivity = ctd.variables['seawater_conductivity'][time_ind]; conductivity_units = ctd.variables['seawater_conductivity'].units

plot_cross_section(time_ctd, pressure, conductivity, ('Pressure', pressure_units, 'Conductivity', conductivity_units,  'CE04OSPS-ctd-cond-xsection'))
plot_cross_section(time_ctd, pressure, density, ('Pressure', pressure_units, 'Density', density_units,  'CE04OSPS-ctd- density-xsection'))
plot_cross_section(time_ctd, pressure, temperature, ('Pressure', pressure_units, 'Temperature', temperature_units,  'CE04OSPS-ctd-temperature-xsection'))
plot_cross_section(time_ctd, pressure, salinity, ('Pressure', pressure_units, 'Salinity', salinity_units,  'CE04OSPS-ctd-salinity-xsection'))


# load fluorometry dataset
flor = nc.Dataset(url_flor)

# convert nc time to datetime and find indices where time is between start and end times set above.
time_flor = nc.num2date(flor.variables['time'][:], flor.variables['time'].units)
time_ind = np.where((time_flor > start_time) & (time_flor < end_time))
time_flor = time_flor[time_ind]
time_flor_num = nc.date2num(time_flor, 'seconds since 1970-01-01')

chl_a = flor.variables['fluorometric_chlorophyll_a'][time_ind]; chl_a_units = flor.variables['fluorometric_chlorophyll_a'].units
cdom = flor.variables['fluorometric_cdom'][time_ind]; cdom_units = flor.variables['fluorometric_cdom'].units
optical_backscatter = flor.variables['flort_d_bback_total'][time_ind]; optical_backscatter_units =flor .variables['flort_d_bback_total'].units
flor_int_pressure = interpolate_list(time_flor_num, time_ctd_num, pressure)

ind_chl_a = reject_outliers(chl_a,2)
ind_cdom = reject_outliers(cdom,2)
ind_obs = reject_outliers(optical_backscatter,1)

plot_cross_section(time_flor[ind_chl_a], flor_int_pressure[ind_chl_a], chl_a[ind_chl_a], ('Pressure', pressure_units, 'Chlorophyll-a', chl_a_units,  'CE04OSPS-flor-chla-xsection'))
plot_cross_section(time_flor[ind_cdom], flor_int_pressure[ind_cdom], cdom[ind_cdom], ('Pressure', pressure_units, 'CDOM', cdom_units,  'CE04OSPS-flor-cdom-xsection'))
plot_cross_section(time_flor[ind_obs], flor_int_pressure[ind_obs], optical_backscatter[ind_obs], ('Pressure', pressure_units, 'Backscatter', optical_backscatter_units,  'CE04OSPS-flor-obsc-xsection'))


# load nitrate dataset
nutnr = nc.Dataset(url_nutnr)

# convert nc time to datetime and find indices where time is between start and end times set above.
time_nutnr = nc.num2date(nutnr.variables['time'][:], nutnr.variables['time'].units)
time_ind = np.where((time_nutnr > start_time) & (time_nutnr < end_time))
time_nutnr = time_nutnr[time_ind]
time_nutnr_num = nc.date2num(time_nutnr, 'seconds since 1970-01-01')

uncorr_nitrate = nutnr.variables['nitrate_concentration'][time_ind]; uncorr_nitrate_units = nutnr.variables['nitrate_concentration'].units
ts_corr_nitrate = nutnr.variables['temp_sal_corrected_nitrate'][time_ind]; ts_corr_nitrate_units = nutnr.variables['temp_sal_corrected_nitrate'].units
nutnr_int_pressure = interpolate_list(time_nutnr_num, time_ctd_num, pressure)

ind_uncorr = reject_outliers(uncorr_nitrate,2)
ind_tscorr = reject_outliers(ts_corr_nitrate,2)

plot_cross_section(time_nutnr[ind_uncorr], nutnr_int_pressure[ind_uncorr], uncorr_nitrate[ind_uncorr], ('Pressure', pressure_units, 'Nitrate Concentration', uncorr_nitrate_units,  'CE04OSPS-nutnr-nitrate-xsection'))
plot_cross_section(time_nutnr[ind_tscorr], nutnr_int_pressure[ind_tscorr], ts_corr_nitrate[ind_tscorr], ('Pressure', pressure_units, 'Temperature/Salinity Corrected Nitrate', ts_corr_nitrate_units,  'CE04OSPS-nutnr-tsnitrate-xsection'))