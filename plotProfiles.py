#! /usr/local/bin/python
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re
import os


def plotProfiles(x, y, args):
    # args = (xName, yName, fName, saveDir)
    xD = x[:]
    yD = y[:]
    
    fig,ax = plt.subplots()
    minorLocator = ticker.AutoMinorLocator()

    ax.plot(xD, yD, 'ro')

    # Image size
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 8.5
    plt.rcParams["figure.figsize"] = fig_size

    # setup axes
    ax.xaxis.set_minor_locator(minorLocator)
    xax = ax.get_xaxis().get_major_formatter()

    y_formatter = ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)
    plt.grid()
    plt.gca().invert_yaxis()

    ax.set_xlabel(args[0] + " (" + x.units + ")") # x label
    ax.set_ylabel(args[1] + ' (' + y.units + ')') # y label
    ax.set_title('Depth Profiles: ' + args[2] + "\n" + args[1]) # title
    sName = str(args[3]) + name + ".png"
    print sName
    plt.savefig(sName,dpi=100) # save figure
    plt.close()

saveDir = '/Users/michaesm/Documents/'

urls = ['http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE01ISSP/09-CTDPFJ000/recovered_cspp/CE01ISSP-SP001-09-CTDPFJ000-ctdpf_j_cspp_instrument_recovered-recovered_cspp/CE01ISSP-SP001-09-CTDPFJ000-ctdpf_j_cspp_instrument_recovered-recovered_cspp.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE02SHBP/06-CTDBPN106/streamed/CE02SHBP-LJ01D-06-CTDBPN106-ctdbp_no_hardware-streamed/CE02SHBP-LJ01D-06-CTDBPN106-ctdbp_no_hardware-streamed.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE04OSBP/06-CTDBPO108/streamed/CE04OSBP-LJ01C-06-CTDBPO108-ctdbp_no_sample-streamed/CE04OSBP-LJ01C-06-CTDBPO108-ctdbp_no_sample-streamed.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Endurance/CE05MOAS/05-CTDGVM000/recovered_host/CE05MOAS-GL384-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CE05MOAS-GL384-05-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUI/03-CTDPFK000/recovered_wfp/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUI/03-CTDPFK000/telemetered/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered/CP02PMUI-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUO/03-CTDPFK000/recovered_wfp/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument_recovered-recovered_wfp.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP02PMUO/03-CTDPFK000/telemetered/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered/CP02PMUO-WFP01-03-CTDPFK000-ctdpf_ckl_wfp_instrument-telemetered.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/telemetered/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CP05MOAS-GL376-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/telemetered/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml',
'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/telemetered/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered/CP05MOAS-GL388-03-CTDGVM000-ctdgv_m_glider_instrument-telemetered.ncml']


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
                plotProfiles(x, y, plotArgs)