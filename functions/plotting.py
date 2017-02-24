#! /usr/bin/env python
__docformat__ = 'restructuredtext en'
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import numpy as np
import urllib2 as url
import pickle
from mpl_toolkits.axes_grid1 import make_axes_locatable
from functions.common import get_global_ranges, reject_outliers


def adcp(time, bins, north, east, title):
    p_data = [north, east]
    horizontal_data = np.concatenate((north['data'], east['data']))
    lim = float("%2.2f" % np.nanpercentile(abs(horizontal_data), 95))

    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
    fig.suptitle(title)
    y_formatter = ticker.ScalarFormatter(useOffset=False)
    # plt.axis([time['data'].min(), time['data'].max(), bins['data'].min(), bins['data'].max()])
    plt.locator_params(nbins=5)
    tick_locator = ticker.MaxNLocator(nbins=6)
    # need to add label to y axis
    for i, ax in enumerate(axes.flat):
        z_data = p_data[i]
        subplot_label = z_data['info']['label']
        cbar_str = z_data['info']['units']
        ax.set_title('{}'.format(subplot_label))
        if i < 2:
            img = ax.pcolormesh(time['data'], bins['data'], p_data[i]['data'], vmin=-lim, vmax=lim, cmap=plt.get_cmap('jet'))
        elif i >= 2:
            tlim = np.nanpercentile(abs(p_data[i]['data']), 90)
            img = ax.pcolormesh(time['data'], bins['data'], p_data[i]['data'], vmin=-tlim, vmax=tlim, cmap=plt.get_cmap('jet'))

        format_axes(ax)
        div = make_axes_locatable(ax)
        cax = div.append_axes("right", size="3%", pad=0.05)
        cbar = plt.colorbar(img, cax=cax)
        cbar.set_label('{}'.format(cbar_str), size=8)
        cbar.locator = tick_locator
        cbar.update_ticks()

    # resize(height=12, width=8.5)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    return fig, axes


def add_global_ranges(ax, data):
    try:
        global_ranges = get_global_ranges(data['info']['platform'], data['info']['node'], data['info']['sensor'], data['info']['var'])
        ax.set_autoscale_on(False)
        g1 = plt.axhline(global_ranges[0], color='g', linestyle='--', label='Global $\min$')
        g2 = plt.axhline(global_ranges[1], color='g', linestyle='--', label='Global $\max$')
    except IndexError:
        print 'No global ranges exist for this reference designator yet.'
        global_ranges = [None, None]
    return global_ranges


def auto_plot(x, y, title, stdev=None, line_style='r-o', g_range=False):
    """
    :param x: x data
    :type x: dictionary
    :param y: y data
    :type y: dictionary
    :param title: plot title
    :type title: basestring
    :param stdev: number of standard deviations you want to remove points from. Leave out of function call or as 'None' if you don't want to reject outliers
    :type stdev: int or Nonetype
    :param line_style: matplotlib linestyle
    :type line_style: basestring
    :return: fig, ax
    :rtype: tuple
    """
    y_shape = y['data'].shape

    if len(y_shape) is 1:
        if np.isnan(y['data']).all():
            fig, ax = nan_plot(title)
        else:
            fig, ax = plot(x, y, title, stdev, line_style, g_range)
    else:
        fig, ax = multilines(x, y, title)
    return fig, ax


# def create_legend(ax, minimum, maximum, outliers, stdev):
#     ax.legend(["Max: %6.2f" % float(int(maximum)) +
#                "\nMin: %6.2f" % float(int(minimum)) +
#                "\nRejected (+- %s stdev ): %s" % (str(stdev), outliers)],
#               loc='best')


def compare_timeseries(t1, y1, t2, y2, g_range=False):
    fig, ax = plt.subplots()
    plt.grid()
    plt.margins(y=.1, x=.1)

    # plot dataset 1
    ax.plot(t1['data'], y1['data'], 'o', markerfacecolor='none', markeredgecolor='r', lw=.75)

    # plot dataset 2
    ax.plot(t2['data'], y2['data'], 'x', markeredgecolor='b', lw=1.5)

    # format x and y axes
    format_axes(ax)

    # Labels
    set_labels(ax, t1['info'], y1['info'])

    # Format legend
    leg_text = ('Recovered\n$\max:$ {:6.4f}\n$\min:$ {:6.4f}'.format(np.nanmax(y1['data']), np.nanmin(y1['data'])),)
    leg_text += ('Telemetered\n$\max:$ {:6.4f}\n $\min:$ {:6.4f}'.format(np.nanmax(y2['data']), np.nanmin(y2['data'])),)

    if g_range:
        gr = add_global_ranges(ax, y1)
        leg_text += ('Global\n$\max$: {} \n$\min$: {}'.format(gr[1], gr[0]),)

    ax.legend(leg_text, loc='best', fontsize=8)
    return fig, ax


def depth_cross_section(x, y, z, s=2, title=None):
    fig, ax = plt.subplots()
    plt.grid()

    ax.invert_yaxis()
    # tlim = np.nanpercentile(abs(z['data']), 95)
    sc = plt.scatter(x['data'], y['data'],
                     s=s,
                     c=z['data'],
                     edgecolors='face')
                     # vmin=)

    # add colorbar
    cb = fig.colorbar(sc, ax=ax, label=z['info']['label'] + " (" + z['info']['units'] + ")")
    cb.formatter.set_useOffset(False)
    cb.update_ticks()

    ax.set_title(title)
    format_axes(ax, x_data=x['data'])
    set_labels(ax, x['info'], y['info'])
    return fig, ax


def format_axes(ax, x_data=None, y_data=None):
    max_xticks = 10
    if x_data is not None:
        ax.set_xlim(x_data[0], x_data[-1])

    if y_data is not None:
        ax.set_ylim(y_data[0], y_data[-1])

    ax.xaxis.set_minor_locator(plt.MaxNLocator(max_xticks))
    # ax.xaxis.set_major_locator(plt.MaxNLocator(max_xticks))
    xax = ax.get_xaxis().get_major_formatter()

    xax.scaled = {
        365.0 : '%Y-%M', # data longer than a year
        30.   : '%Y-%m\n%d', # set the > 1m < 1Y scale to Y-m
        1.0   : '%m/%d', # set the > 1d < 1m scale to Y-m-d
        1./24.: '%m/%d', # set the < 1d scale to H:M
        1./48.: '%m-%d\n%H:%M:%S',
    }

    y_formatter = ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)


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


def multilines(x, y, title):
    fig, ax = plt.subplots()
    plt.grid()

    for column in y['data'].T:
        plt.plot(x['data'], column, linewidth=2)

    ax.set_title(title)
    format_axes(ax, x['data'], y['data'])
    set_labels(ax, x['info'], y['info'])
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


def plot(x, y, title, stdev = None, line_style='r-o', g_ranges=False):
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
        outlier_text = ''
    else:
        # if len(np.unique(y['data'])) is 1:
        #     y_max = np.unique(y['data'])[0]
        #     y_min = np.unique(y['data'])[0]
        #     outliers = 0
        # else:
        ind = reject_outliers(y['data'], stdev)
        y['data'] = y['data'][ind]
        x['data'] = x['data'][ind]
        outliers = str(len(ind) - sum(ind))
        outlier_text = 'n removed $\pm$ {}$\sigma: $ {}'.format(stdev, outliers)

    fig, ax = plt.subplots()
    # ax.set_autoscale_on(False)
    plt.grid()
    plt.plot(x['data'], y['data'], line_style, linewidth=2, markersize=2)

    ax.set_title(title)

    # Format legend
    try:
        leg_text = ('$\max:$ {:6.4f}\n$\min:$ {:6.4f}\n{}'.format(np.nanmax(y['data']), np.nanmin(y['data']), outlier_text),)
    except ValueError:
        leg_text = ()

    if g_ranges:
        gr = add_global_ranges(ax, y)
        leg_text += ('Global Ranges\n$\max$: {} \n$\min$: {}'.format(gr[1], gr[0]),)

    ax.legend(leg_text, loc='best', fontsize=8)
    format_axes(ax)
    set_labels(ax, x['info'], y['info'])
    return fig, ax


def plot_outlier_comparison(x, y, title, stdev = 1, line_style='r-o', g_range=False):
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
    ind = reject_outliers(y['data'], stdev)
    y['data'] = y['data']
    x['data'] = x['data']
    outliers = str(len(ind) - sum(ind))
    outlier_text = 'n removed $\pm$ {}$\sigma: $ {}'.format(stdev, outliers)

    ax1 = plt.subplot(211)
    plt.plot(x['data'], y['data'], line_style, linewidth=2, markersize=2)
    plt.grid()
    format_axes(ax1)

    # Format legend
    leg_text = ('$\max:$ {:6.4f}\n$\min:$ {:6.4f}\n{}'.format(np.nanmax(y['data'][ind]), np.nanmin(y['data'][ind]), outlier_text),)

    ax2 = plt.subplot(212, sharex=ax1)
    plt.grid()
    plt.plot(x['data'][ind], y['data'][ind], line_style, linewidth=2, markersize=2)
    format_axes(ax2)
    # plt.setp(ax2.get_xticklabels(), fontsize=8)

    ax1.set_title(title)
    # ax2.set_title('Global Ranges $\max$: {} $\min$: {}'.format(gr[1], gr[0]), fontsize=8)
    if g_range:
        gr = add_global_ranges(ax2, y)
        leg_text += ('Global Ranges $\max$: {} $\min$: {}'.format(gr[1], gr[0]),)
    ax2.legend(leg_text, loc='best', fontsize=8)

    ax1.set_ylabel(y['info']['label'] + " (" + y['info']['units'] + ")")
    ax2.set_ylabel(y['info']['label'] + " (" + y['info']['units'] + ")")
    ax2.set_xlabel(x['info']['label'] + " (" + x['info']['units'] + ")")
    return ax1, ax2
    # format_axes(ax)
    # set_labels(ax1, x['info'], y['info'])
    # set_labels(ax2, x['info'], y['info'])
    # return fig, ax



def resize(width=12, height=8.5):
    """
    Resize the image to the size of a standard 8.5x11 sheet of paper and set
    axes margins to have a buffer of 10 percent
    :param plt: The plot handle of the image you want to resize
    :return: None
    """
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = width
    fig_size[1] = height
    plt.rcParams["figure.figsize"] = fig_size
    # plt.rcParams["axes.xmargin"] = 0.1
    # plt.rcParams["axes.ymargin"] = 0.1


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