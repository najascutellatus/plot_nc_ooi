#! /usr/local/bin/python
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import re
import os
import datetime as dt


def get_time_ind(tArray, t0, t1):
    # This function returns data (x,y) between start time and end time
    # mpl datenum array, y data, start datetime, end datetime
    # tInd = tArray[np.where((tArray>= t0) & (tArray <=t1))]
    tInd = np.where((tArray>= t0) & (tArray <=t1))
    return tInd

def plot_profiles1(x, y, t, args):
    # xM = np.ma.masked_equal(x, 0)
    # xM = x
    tM = nc.num2date(t[:], t.units)
    yM = np.ma.masked_where(0.0 >= y, y)
    xM = np.ma.masked_where(0.0 >= y, x)
    tM = np.ma.masked_where(0.0 >= y, tM)

    # yM = np.ma.masked_equal(yM, 0)

    # args = (xName, yName, fName, saveDir)
    f, ax = plt.subplots(2,4, sharex=True, sharey=True)
    plt.locator_params(nbins=4)
    plt.grid(True)
    ax[0,0].invert_yaxis()
    # Image size
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 8.5
    plt.rcParams["figure.figsize"] = fig_size

    for key, value in seasons1.iteritems():
        try:
            ind_time = get_time_ind(tM, value[0], value[1])
            xD = xM[ind_time]
            yD = yM[ind_time]
            tD = tM[ind_time]
            tN = tM[ind_time]
            sub_title = key
        except:
            print "No data found for key. Plotting all data panel'"
            xD = xM[:]
            yD = yM[:]
            tD = t[:]
            sub_title = " all profiles"

        # colors = np.rand
        # ax[value[2], value[3]].plot(xD, yD, 'ro', markersize=3)
        colors = cm.rainbow(np.linspace(0,1, len(tN)))
        ax[value[2], value[3]].scatter(xD, yD, s=2, c=colors, edgecolors='face')
        ax[value[2], value[3]].set_title(sub_title)
        ax[value[2], value[3]].grid(True)
        ax[value[2], value[3]].set_ylabel(args[1] + ' (' + y.units + ')', fontsize=8) # y label


        # fig,ax = plt.subplots()
        # minorLocator = ticker.AutoMinorLocator()

        # ax.plot(xD, yD, 'ro')

        # # setup axes
        # ax.xaxis.set_minor_locator(minorLocator)
        # xax = ax.get_xaxis().get_major_formatter()
        #
        # y_formatter = ticker.ScalarFormatter(useOffset=False)
        # ax.yaxis.set_major_formatter(y_formatter)
        #
        # plt.grid()
        # plt.gca().invert_yaxis()


        # ax.set_title('Depth Profiles: ' + args[2] + "\n" + args[1]) # title
    plt.setp([a.get_xticklabels() for a in ax[0, :]], visible=False)
    plt.setp([a.set_xlabel(' ') for a in ax[0,:]], visible=False)
    # plt.setp([a.locator_params(tight=True, nbins=4) for a in ax])
    ax[1,0].set_xlabel(args[0] + " (" + x.units + ")")
    ax[1,2].set_xlabel(args[0] + " (" + x.units + ")")
    # ax.locator_params(nbins=4)
    # plt.setp([a.invert_yaxis() for a in ax])
    f.suptitle(args[2], fontsize=10)
    # plt.setp([a.get_yticklabels() for a in ax[:, 1]], visible=False)

    save_name = str(args[3]) + args[2] + "-1.png"
    print save_name

    plt.savefig(save_name,dpi=100) # save figure
    plt.close()

def plot_profiles2(x, y, t, args):
    xM = np.ma.masked_where(x==0, x)
    yM = np.ma.masked_where(y==0, y)
    # args = (xName, yName, fName, saveDir)
    f, ax = plt.subplots(2,2, sharex=True, sharey=True)
    ax[0,0].invert_yaxis()
    # Image size
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 8.5
    plt.rcParams["figure.figsize"] = fig_size

    for key, value in seasons2.iteritems():
        try:
            ind_time = get_time_ind(t, value[0], value[1])
            xD = xM[ind_time]
            yD = yM[ind_time]
            sub_title = key + " profiles\n"
        except:
            print "No data found for key. Plotting all data panel'"
            xD = xM[:]
            yD = yM[:]
            sub_title = " all profiles"

        ax[value[2], value[3]].plot(xD, yD, 'ro')
        ax[value[2], value[3]].set_title(sub_title)
        # ax[value[2], value[3]].set_xlabel(args[0] + " (" + x.units + ")") # x label
        ax[value[2], value[3]].set_ylabel(args[1] + ' (' + y.units + ')') # y label

        # fig,ax = plt.subplots()
        # minorLocator = ticker.AutoMinorLocator()

        # ax.plot(xD, yD, 'ro')

        # # setup axes
        # ax.xaxis.set_minor_locator(minorLocator)
        # xax = ax.get_xaxis().get_major_formatter()
        #
        # y_formatter = ticker.ScalarFormatter(useOffset=False)
        # ax.yaxis.set_major_formatter(y_formatter)
        #
        # plt.grid()
        # plt.gca().invert_yaxis()


        # ax.set_title('Depth Profiles: ' + args[2] + "\n" + args[1]) # title
    plt.setp([a.get_xticklabels() for a in ax[0, :]], visible=False)
    plt.setp([a.set_xlabel(' ') for a in ax[0,:]], visible=False)
    ax[1,0].set_xlabel(args[0] + " (" + x.units + ")")
    # plt.setp([a.invert_yaxis() for a in ax])
    f.suptitle(args[2], fontsize=10)
    # plt.setp([a.get_yticklabels() for a in ax[:, 1]], visible=False)

    save_name = str(args[3]) + args[2] + "-2.png"
    print save_name

    plt.savefig(save_name,dpi=100) # save figure
    plt.close()

saveDir = '/Users/michaesm/Documents/'

urls = ['http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/telemetered/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml']


# urls = ['http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE01ISSP/09-CTDPFJ000/recovered_cspp/CE01ISSP-SP001-09-CTDPFJ000-ctdpf_j_cspp_instrument_recovered-recovered_cspp/CE01ISSP-SP001-09-CTDPFJ000-ctdpf_j_cspp_instrument_recovered-recovered_cspp.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE02SHBP/06-CTDBPN106/streamed/CE02SHBP-LJ01D-06-CTDBPN106-ctdbp_no_hardware-streamed/CE02SHBP-LJ01D-06-CTDBPN106-ctdbp_no_hardware-streamed.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE04OSBP/06-CTDBPO108/streamed/CE04OSBP-LJ01C-06-CTDBPO108-ctdbp_no_sample-streamed/CE04OSBP-LJ01C-06-CTDBPO108-ctdbp_no_sample-streamed.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE05MOAS/05-CTDGVM000/recovered_host/CE05MOAS-GL384-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CE05MOAS-GL384-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUI/03-CTDPFK000/recovered_wfp/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUI/03-CTDPFK000/telemetered/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUO/03-CTDPFK000/recovered_wfp/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUO/03-CTDPFK000/telemetered/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/telemetered/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/telemetered/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml',
#         'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/telemetered/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml']

seasons1 = {'winter_13/14': [dt.datetime(2013,12,1,0,0,0), dt.datetime(2014,3,1,0,0,0), 0,0],
            'spring_2014':[dt.datetime(2014,3,1,0,0,0), dt.datetime(2014,6,1,0,0,0), 0,1],
            'summer_2014': [dt.datetime(2014,6,1,1,0,0), dt.datetime(2014,9,1,1,0,0), 0,2],
            'fall_2014': [dt.datetime(2014,9,1,0,0,0), dt.datetime(2014,12,1,0,0,0), 0,3],
            'winter_14/15': [dt.datetime(2014,12,1,0,0,0), dt.datetime(2015,3,1,0,0,0), 1,0],
            'spring_2015': [dt.datetime(2015,3,1,0,0,0), dt.datetime(2015,6,1,0,0,0), 1,1],
            'summer_2015': [dt.datetime(2015,6,1,1,0,0), dt.datetime(2015,9,1,1,0,0), 1,2],
            'fall_2015': [dt.datetime(2015,9,1,0,0,0), dt.datetime(2015,12,1,0,0,0), 1,3]}

global seasons1
global seasons2

pressures = {'ctdbp_cdef_instrument_recovered': 'ctdbp_seawater_pressure',
             'ctdbp_cdef_dcl_instrument_recovered': 'pressure',
             'ctdbp_cdef_dcl_instrument-': 'pressure',
             'ctdgv_m_glider_instrument-': 'sci_water_pressure',
             'ctdgv_m_glider_instrument_recovered': 'sci_water_pressure',
             'ctdpf_j_cspp_instrument_recovered': 'pressure',
             'ctdpf_j_cspp_instrument-': 'pressure',
             'ctdpf_ckl_wfp_instrument_recovered': 'ctdpf_ckl_seawater_pressure',
             'ctdpf_ckl_wfp_instrument-': 'ctdpf_ckl_seawater_pressure'}

streamKeys = list(pressures.keys())
reStream = re.compile('|'.join(streamKeys))
# yVars = [s for s in yVars if not reV.search(s)]

datastrs = ['time', 'date', 'provenance', 'counts', 'volts', 'qc', 'deployment', 'timestamp','id',
            '_qc_executed', '_qc_results', 'pressure', 'lat', 'lon', 'depth', 'obs', 'm_present']

reV = re.compile('|'.join(datastrs))

for url in urls:
    print url
    for i in streamKeys:
        if i in url:
            print i
            f = nc.Dataset(url)
            time = f.variables['time']
            # print time[0]
            fN = f.id
            yN = pressures[i]
            y = f.variables[yN]

            varList = []
            for varNum in f.variables:
                varList.append(str(varNum))

            xVars = [s for s in varList if not reV.search(s)]

            for xN in xVars:
                x = f.variables[xN]
                fName = fN + '_profiles_' + xN
                plotArgs = (xN, yN, fName, saveDir)
                plot_profiles1(x, y, time, plotArgs)
                # plot_profiles2(x, y, time, plotArgs)