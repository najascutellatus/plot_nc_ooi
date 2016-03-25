#! /usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime as dt
import os
import numpy as np
import urllib2 as url
import pickle
import pandas as pd
from dateutil.rrule import *
from dateutil.relativedelta import relativedelta


def create_dir(new_dir):
    # Check if dir exists.. if it doesn't... create it.
    if not os.path.isdir(new_dir):
        try:
            os.makedirs(new_dir)
        except OSError:
            if os.path.exists(new_dir):
                pass
            else:
                raise


def auto_plot(x, y, title, stdev=3, line_style='r-o'):
    y_shape = y['data'].shape

    if len(y_shape) is 1:
        if np.isnan(y['data']).all():
            fig, ax = nan_plot(title)
        else:
            fig, ax = plot(x, y, title, stdev, line_style)
    else:
        fig, ax = multilines(x, y, title)
    return fig, ax


def multilines(x, y, title):
    fig, ax = plt.subplots()
    plt.grid()

    for column in y['data'].T:
        plt.plot(x['data'], column, linewidth=2)

    ax.set_title(title)
    format_axes(ax, x['data'], y['data'])
    set_labels(ax, x['info'], y['info'])
    return fig, ax


def depth_cross_section(x, y, z):
    fig, ax = plt.subplots()
    plt.grid()

    ax.invert_yaxis()

    # Format the date axis
    # plt.locator_params(nbins=4)
    # df = m_date.DateFormatter('%Y-%m-%d')
    # ax.xaxis.set_major_formatter(df)
    # fig.autofmt_xdate()

    sc = plt.scatter(x['data'], y['data'],
                     s=2,
                     c=z['data'],
                     edgecolors='face')

    # add colorbar
    cb = fig.colorbar(sc,
                      ax=ax,
                      label=z['info']['label'] + " (" + z['info']['units'] + ")")
    cb.formatter.set_useOffset(False)
    cb.update_ticks()

    format_axes(ax, x['data'], y['data'])
    set_labels(ax, x['info'], y['info'])
    return fig, ax


def format_axes(ax, x_data, y_data):
    # ax.set_xlim(x_data[0], x_data[-1])
    # ax.set_ylim(y_data[0], y_data[-1])
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    xax = ax.get_xaxis().get_major_formatter()

    xax.scaled = {
        365.0 : '%Y-%M', # data longer than a year
        30.   : '%Y-%m\n%d', # set the > 1m < 1Y scale to Y-m
        1.0   : '%b-%d\n%H:%M', # set the > 1d < 1m scale to Y-m-d
        1./24.: '%b-%d\n%H:%M', # set the < 1d scale to H:M
        1./48.: '%b-%d\n%H:%M:%S',
    }

    y_formatter = ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)


def get_time_ind(array, t0, t1):
    """
    Returns data (x,y) between start time and end time
    :param array: Numpy array of datenums
    :param t0: Start datetime
    :param t1: End datetime
    :return: Index between start and end datetimes
    """
    time_ind = np.where((array >= t0) & (array <= t1))
    return time_ind


def load_variable_dict(var='eng'):
    """
    Load a pre-populated dictionary containing a list of either science or
    engineering variable names associated with a specific stream
    :param var: 'eng' for engineering variables. 'sci' for science variables
    :return: A dictionary of streams containing a sub-dictionaries of variables
    """

    if var == 'eng':
        pkl_url = 'https://raw.githubusercontent.com/ooi-data-review/ooi-parameters-dict/master/ooi_nonscience_parameters.pkl'
    elif var == 'sci':
        pkl_url = 'https://raw.githubusercontent.com/ooi-data-review/ooi-parameters-dict/master/ooi_plotting_parameters.pkl'

    fp = url.urlopen(pkl_url)
    var_dict = pickle.load(fp)
    return var_dict


def create_legend(ax, minimum, maximum, outliers, stdev):
    ax.legend(["Max: %6.2f" % float(int(maximum)) +
               "\nMin: %6.2f" % float(int(minimum)) +
               "\nRejected (+- %s stdev ): %s" % (str(stdev), outliers)],
              loc='best')


def plot(x, y, title, stdev = None, line_style='r-o'):
    """

    :param x: Dictionary must be in the form:
    {'data': numpy data array ,
    'info': {'label': axis label, 'units': axis units'}}
    :param y:
    :param file_name:
    :param save_dir:
    :param line_style:
    :return:
    """

    if stdev is None:
        y = y
    else:
        if len(np.unique(y['data'])) is 1:
            y_max = np.unique(y['data'])[0]
            y_min = np.unique(y['data'])[0]
            outliers = 0
        else:
            ind = reject_outliers(y['data'], stdev)
            y['data'] = y['data'][ind]
            x['data'] = x['data'][ind]
            y_max = y['data'].max()
            y_min = y['data'].min()
            outliers = str(len(ind) - sum(ind))

    fig, ax = plt.subplots()
    plt.grid()
    plt.plot(x['data'], y['data'], line_style, linewidth=2, markersize=2)

    create_legend(ax, y_min, y_max, outliers, stdev)
    ax.set_title(title)
    format_axes(ax, x['data'], y['data'])
    set_labels(ax, x['info'], y['info'])
    return fig, ax


def pcolor(x, y, z):
    fig, ax = plt.subplots()
    pc = ax.pcolor(x, y, z)
    plt.colorbar(pc)
    return fig, ax


def nan_plot(title):
    fig, ax = plt.subplots()
    left, width = .25, .5
    bottom, height = .25, .5
    right = left + width
    top = bottom + height
    ax.text(0.5*(left + right), 0.5*(bottom + top), 'Y-Axis contained all NaNs',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes)
    ax.set_title(title)
    return fig, ax


def reject_outliers(data, m=3):
    """
    Reject outliers standard deviations of the mean.
    :param data: Numpy array containing data
    :param m: Number of standard deviations from the mean. Default: 3
    :return: Index of the outliers contained in the numpy array
    """
    # function to reject outliers beyond 3 standard deviations of the mean.
    # data: numpy array containing data
    # m: the number of standard deviations from the mean. Default: 3
    return abs(data - np.mean(data)) < m * np.std(data)


def resize(width=12, height=8.5):
    """
    Resize the image to the size of a standard 8.5x11 sheet of paper and set
    axes margins to have a buffer of 10 percent
    :param plt: The plot handle of the image you want to resize
    :return: None
    """
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 8.5
    plt.rcParams["figure.figsize"] = fig_size
    plt.rcParams["axes.xmargin"] = 0.1
    plt.rcParams["axes.ymargin"] = 0.1


def save_fig(save_dir, file_name, res=300):
    """
    Save figure to a directory with a resolution of 300 DPI
    :param save_dir: Location of the directory to save the file
    :param file_name: The name of the file you want to save
    :param res: Resolution in DPI of the image you want to save
    :return: None
    """
    save_file = os.path.join(save_dir, file_name)
    plt.savefig(str(save_file) + '.png', dpi=res)
    plt.close()


def set_labels(ax, x_info, y_info):
    """
    Set X and Y labels of the plot
    :param ax: Axes object of the image
    :param x_info: Dictionary containing two keys: label and units
    :param y_info: Dictionary containing two keys: label and units
    :return: None
    """
    ax.set_ylabel(y_info['label'] + " (" + y_info['units'] + ")")
    ax.set_xlabel(x_info['label'] + " (" + x_info['units'] + ")")


def get_rounded_start_and_end_times(timestamp):
    ts0 = to_the_second(pd.to_datetime(timestamp.min()))
    ts1 = to_the_second(pd.to_datetime(timestamp.max()))
    ts_start = round_to_best_hour(ts0)
    ts_end = round_to_best_hour(ts1)
    return ts_start, ts_end


def round_to_best_hour(t):

    delta = dt.timedelta(minutes=t.minute, seconds=t.second,
                         microseconds=t.microsecond)

    down = t - delta # subtract seconds from the time
    up = t + dt.timedelta(seconds=3600) - delta

    if abs(t - up) > abs(t - down):
        return down
    else:
        return up


def to_the_second(ts):
    return pd.Timestamp(long(round(ts.value, -9)))


# def date_range(start_date, end_date, increment, period):
#     # period = 'years', 'months', 'weeks', 'days', 'hours'
#     result = []
#     nxt = start_date
#     delta = relativedelta(**{period: increment})
#     while nxt <= end_date:
#         result.append(nxt)
#         nxt += delta
#     return result
#
#
# def build_times(t0, t1, secs):
#     hourly = date_range(t0, t1, )
#     for freq in [DAILY, WEEKLY, MONTHLY]:
#         month = range_times(freq, t0, t1)
#         # time_array = np.concatenate((hour,day,week,month,record), axis=0)
#     # return time_array
#
#
# def range_times(freq, time_start, time_end):
#     # Function returns a list of times between two datetimes
#     # Where freq must be one of YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY
#     time = list(rrule(freq, dtstart=time_start, until=time_end))
#     arr = np.empty((0,2))
#     for time_start, time_end in zip(time, time[1:]):
#         arr = np.append(arr, np.array([[time_start, time_end]]),0)
#     return arr


#     # setup axes
#     if args.lock: # lock y-limits axes across time period
#         plt.ylim((yTuple[3], yTuple[4]))



