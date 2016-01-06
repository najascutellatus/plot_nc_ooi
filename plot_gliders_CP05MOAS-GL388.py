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

def plot_depth_cross_section(x, y, z, args):
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
    fig.colorbar(sc, ax=ax, label=args[2] + " (" + args[3] + ")")

    # plot labels
    # ax.set_title(args)
    plt.ylabel(args[0] + ' (' + args[1] + ')') # y label
    plt.xlabel("Time (GMT)")

    plt.savefig(args[4], dpi=100) # save figure
    plt.close()

def reject_outliers(data, m=2):
    return abs(data - np.mean(data)) < m * np.std(data)



url_ctd='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-1/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml'
url_dost='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-1/Coastal_Pioneer/CP05MOAS/04-DOSTAM000/recovered_host/CP05MOAS-GL388-04-DOSTAM000-dosta_abcdjm_glider_recovered-recovered_host/CP05MOAS-GL388-04-DOSTAM000-dosta_abcdjm_glider_recovered-recovered_host.ncml'
url_flor='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-1/Coastal_Pioneer/CP05MOAS/02-FLORTM000/recovered_host/CP05MOAS-GL388-02-FLORTM000-flort_m_glider_recovered-recovered_host/CP05MOAS-GL388-02-FLORTM000-flort_m_glider_recovered-recovered_host.ncml'
url_par='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-1/Coastal_Pioneer/CP05MOAS/05-PARADM000/recovered_host/CP05MOAS-GL388-05-PARADM000-parad_m_glider_recovered-recovered_host/CP05MOAS-GL388-05-PARADM000-parad_m_glider_recovered-recovered_host.ncml'


start_time = datetime.datetime(2014, 12, 1, 20, 0, 0)
end_time = datetime.datetime(2014, 12, 9, 0, 0, 0)


# load CTD dataset
ctd = nc.Dataset(url_ctd)

# convert nc time to datetime and find indices where time is between start and end times set above.
time_ctd = nc.num2date(ctd.variables['time'][:], ctd.variables['time'].units)
time_ind = np.where((time_ctd > start_time) & (time_ctd < end_time))
time_ctd = time_ctd[time_ind]
time_ctd_num = nc.date2num(time_ctd, 'seconds since 1970-01-01')

pressure = ctd.variables['sci_water_pressure'][time_ind]; pressure_units = ctd.variables['sci_water_pressure'].units

density = ctd.variables['sci_seawater_density'][time_ind]; density_units = ctd.variables['sci_seawater_density'].units
salinity = ctd.variables['sci_water_pracsal'][time_ind]; salinity_units = ctd.variables['sci_water_pracsal'].units
temperature = ctd.variables['sci_water_temp'][time_ind]; temperature_units = ctd.variables['sci_water_temp'].units
conductivity = ctd.variables['sci_water_cond'][time_ind]; conductivity_units = ctd.variables['sci_water_cond'].units

plot_depth_cross_section(time_ctd, pressure, conductivity, ('Pressure', pressure_units, 'Conductivity', conductivity_units,  'CP05MOAS-GL388-ctd-cond-xsection'))
plot_depth_cross_section(time_ctd, pressure, density, ('Pressure', pressure_units, 'Density', density_units,  'CP05MOAS-GL388-ctd-density-xsection'))
plot_depth_cross_section(time_ctd, pressure, temperature, ('Pressure', pressure_units, 'Temperature', temperature_units,  'CP05MOAS-GL388-ctd-temperature-xsection'))
plot_depth_cross_section(time_ctd, pressure, salinity, ('Pressure', pressure_units, 'Salinity', salinity_units,  'CP05MOAS-GL388-ctd-salinity-xsection'))


# load fluorometry dataset
flor = nc.Dataset(url_flor)

# convert nc time to datetime and find indices where time is between start and end times set above.
time_flor = nc.num2date(flor.variables['time'][:], flor.variables['time'].units)
time_ind = np.where((time_flor > start_time) & (time_flor < end_time))
time_flor = time_flor[time_ind]
time_flor_num = nc.date2num(time_flor, 'seconds since 1970-01-01')

chl_a = flor.variables['sci_flbbcd_chlor_units'][time_ind]; chl_a_units = flor.variables['sci_flbbcd_chlor_units'].units
cdom = flor.variables['sci_flbbcd_cdom_units'][time_ind]; cdom_units = flor.variables['sci_flbbcd_cdom_units'].units
obs = flor.variables['flort_m_bback_total'][time_ind]; obs_units =flor.variables['flort_m_bback_total'].units
int_ctd_pressure = flor.variables['int_ctd_pressure'][time_ind]; int_ctd_pressure_units = flor.variables['int_ctd_pressure'].units

plot_depth_cross_section(time_flor, int_ctd_pressure, chl_a, ('Pressure', pressure_units, 'Chlorophyll-a', chl_a_units,  'CP05MOAS-GL388-flor-chla-xsection'))
plot_depth_cross_section(time_flor, int_ctd_pressure, cdom, ('Pressure', pressure_units, 'CDOM', cdom_units,  'CP05MOAS-GL388-flor-cdom-xsection'))
plot_depth_cross_section(time_flor, int_ctd_pressure, obs, ('Pressure', pressure_units, 'Optical Backscatter', obs_units,  'CP05MOAS-GL388-flor-obsc-xsection'))


# load oxygen dataset
dost = nc.Dataset(url_dost)

# convert nc time to datetime and find indices where time is between start and end times set above.
time_dost = nc.num2date(dost.variables['time'][:], dost.variables['time'].units)
time_ind = np.where((time_dost > start_time) & (time_dost < end_time))
time_dost = time_dost[time_ind]
time_dost_num = nc.date2num(time_dost, 'seconds since 1970-01-01') # convert to a number for interpolation

oxygen = dost.variables['sci_oxy4_oxygen'][time_ind]; oxygen_units = dost.variables['sci_oxy4_oxygen'].units
saturation = dost.variables['sci_oxy4_saturation'][time_ind]; saturation_units = dost.variables['sci_oxy4_saturation'].units
int_ctd_pressure = dost.variables['int_ctd_pressure'][time_ind]; int_ctd_pressure_units = dost.variables['int_ctd_pressure'].units

plot_depth_cross_section(time_dost, int_ctd_pressure, oxygen, ('Pressure', pressure_units, 'Oxygen', oxygen_units,  'CP05MOAS-GL388-dost-oxygen-xsection'))
plot_depth_cross_section(time_dost, int_ctd_pressure, saturation, ('Pressure', pressure_units, 'Oxygen Saturation', saturation_units,  'CP05MOAS-GL388-dost-saturation-xsection'))


# load par dataset
par = nc.Dataset(url_par)

time_par = nc.num2date(par.variables['time'][:], par.variables['time'].units)
time_ind = np.where((time_par > start_time) & (time_par < end_time))
time_par = time_par[time_ind]
time_par_num = nc.date2num(time_par, 'seconds since 1970-01-01')

bsipar = par.variables['sci_bsipar_par'][time_ind]; bsipar_units = par.variables['sci_bsipar_par'].units
int_ctd_pressure = par.variables['int_ctd_pressure'][time_ind]; int_ctd_pressure_units = par.variables['int_ctd_pressure'].units
plot_depth_cross_section(time_par, int_ctd_pressure, bsipar, ('Pressure', pressure_units, 'PAR', bsipar_units,  'CP05MOAS-GL388-par-bsipar-xsection'))

