#! /usr/local/bin/python

import os,sys,time
import netCDF4 as nc
import numpy as np
# import pylab
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mDate
import matplotlib.ticker as ticker
import pytz
from dateutil.rrule import *
import argparse
from xml.dom import minidom
import os
import urllib2
import re
import pickle

'''
This script is used to generates plots from any netcdf file containing a time 
variable and containing other data.

You can create time series, depth profiles, and regular line plots
'''

################################################################################
# Functions 
################################################################################
def split_url(url):
    m_url = url.rsplit('/', 1)
    m_url = m_url[0] + '/'
    return m_url

def grab_xml(url):
    usock = urllib2.urlopen(url)
    xmlData = minidom.parse(usock)
    usock.close()
    return xmlData

def scan_xml(xmlData):
  arrays=[]
  arrays_xml = xmlData.getElementsByTagName('catalogRef')
  for arrays_xml in arrays_xml:
      stitle = arrays_xml.getAttribute('xlink:href')
      arrays.append(str(stitle))
  return arrays

def get_datasetURL(xmlData):
    arrays=[]
    arrays_xml = xmlData.getElementsByTagName('dataset')
    for array in arrays_xml:
        stitle = array.getAttribute('urlPath')
        arrays.append(str(stitle))
    return arrays


def iterate_items(url):
    mainURL = split_url(url)
    mainXML = grab_xml(url)
    arrays = scan_xml(mainXML)
    tUrls = [mainURL + x for x in arrays]
    return tUrls

def iterate_data(url):
    mainURL = split_url(url)
    mainXML = grab_xml(url)
    arrays = get_datasetURL(mainXML)
    # tUrls = [mainURL + x for x in arrays]
    return arrays

def createLineSpace():
    print "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-="

def definePlot():
    plotDict = {}
    plotDict['1'] = 'timeseries'
    plotDict['2'] = 'profile'
    plotDict['3'] = 'line'
    print "Select Plot Type: "
    print "Time Series (Time vs. Variable): 1"
    print "Depth Profile (Time vs. Pressure colored by Sensor Variable): 2"
    print "Line Chart (x Variable vs. y Variable): 3" 
    pltType = raw_input("Enter plot type number (Enter <1>): ") or '1'
    return plotDict[pltType]

def getSingleVariable(library):
    if len(library) == 1:
        print "Only 1 variable present."
        print "Automatically selecting '" + str(library[0]) + "' as y-axis ."
        singleVarName = library[0]
    elif len(library) > 1:
        # Only allow one variable chosen
        for variable in library:
            var = str(raw_input("Variable: %s"%variable + " <n>: ")) or 'n' 
            if var == 'y': #if prompt is equal to 'y'
                singleVarName = variable # create variable for x-axis 
                break #once the variable is selected, break out of the loop
    return singleVarName
    
def getMultipleVariables(library):
    multiVarLib = [] # Create empty list for y variables and metadata
    for variable in library:
        var = str(raw_input("Variable: %s"%variable + " <n> : ")) or 'n'
        if var == 'y':
            multiVarLib.append(variable)
    return multiVarLib

# def plotProfiles(x, y, yTuple, saveDir):
#     ## function to create time series plot
#     ## x: profiled variable, y: pressure or depth
#     ## yTuple: ('variable name', 'units'), saveDir
#
#     ymin = np.nanmin(y)
#     ymax = np.nanmax(y)
#     nMa = np.ma.count_masked(y)
#
#     fig,ax = plt.subplots()
#     minorLocator = ticker.AutoMinorLocator()
#
#     ax.plot(x, y, args.lineStyle)
#
#     # Image size
#     fig_size = plt.rcParams["figure.figsize"]
#     fig_size[0] = 12
#     fig_size[1] = 8.5
#     plt.rcParams["figure.figsize"] = fig_size
#
#     # setup axes
#     if args.lock: # lock y-limits axes across time period
#         plt.ylim((yTuple[3], yTuple[4]))
#     ax.xaxis.set_minor_locator(minorLocator)
#     xax = ax.get_xaxis().get_major_formatter()
#
#     y_formatter = ticker.ScalarFormatter(useOffset=False)
#     ax.yaxis.set_major_formatter(y_formatter)
#     plt.grid()
#
#     # setup labels and title
#     # ts1 = min(x); ts2 = max(x)
#     # ts1 = mDate.num2date(ts1); ts2 = mDate.num2date(ts2)
#     # tStr = ts1.strftime('%Y-%m-%dT%H%M%S') + '_' + ts2.strftime('%Y-%m-%dT%H%M%S')
#     # tStrTitle = ts1.strftime('%Y-%m-%d %H:%M:%S') + ' to ' + ts2.strftime('%Y-%m-%d %H:%M:%S')
#     # ax.legend(["Maximum: %f" % ymax + "\nMinimum: %f" % ymin + "\nMasked: %f" % nMa], loc='best')
#     ax.set_xlabel('Time (UTC)') # x label
#     ax.set_ylabel(str(yTuple[0]) + ' (' + yTuple[1] + ')') # y label
#     ax.set_title(fName + '\n' + tStrTitle) # title
#
#     fListing = 0
#     tFormatDir = timeRecordIndicator(ts1, ts2)
#
#     if fListing == 1:
#         tempDir = os.path.join(saveDir, tFormatDir)
#         createDir(tempDir)
#         saveFileName = yTuple[0] + '-ts-' + tStr
#         sDir = os.path.join(tempDir, saveFileName)
#     else:
#         createDir(saveDir)
#         saveFileName = yTuple[0] + '-ts-' + tFormatDir + '-' + tStr
#         sDir = os.path.join(saveDir, saveFileName)
#
#
#     plt.savefig(str(sDir),dpi=int(args.res)) # save figure
#     plt.close()

def plotTimeSeries(x, y, yTuple, saveDir):
    ## function to create time series plot
    ## x: array of datetimes, y: data to plot
    ## yTuple: ('variable name', 'units'), saveDir
    x = mDate.date2num(x) # convert datetime to matplotlib time
    ymin = np.nanmin(y)
    ymax = np.nanmax(y)
    nMa = np.ma.count_masked(y)

    fig,ax = plt.subplots()
    minorLocator = ticker.AutoMinorLocator()

    ax.plot_date(x, y, args.lineStyle, xdate=True, ydate=False, tz=pytz.utc)

    # Image size
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 8.5
    plt.rcParams["figure.figsize"] = fig_size

    # setup axes
    if args.lock: # lock y-limits axes across time period
        plt.ylim((yTuple[3], yTuple[4]))
    ax.xaxis.set_minor_locator(minorLocator)
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
    plt.grid()

    # setup labels and title
    ts1 = min(x); ts2 = max(x)
    ts1 = mDate.num2date(ts1); ts2 = mDate.num2date(ts2)
    tStr = ts1.strftime('%Y-%m-%dT%H%M%S') + '_' + ts2.strftime('%Y-%m-%dT%H%M%S')
    tStrTitle = ts1.strftime('%Y-%m-%d %H:%M:%S') + ' to ' + ts2.strftime('%Y-%m-%d %H:%M:%S')
    ax.legend(["Maximum: %f" % ymax + "\nMinimum: %f" % ymin + "\nMasked: %f" % nMa], loc='best')
    ax.set_xlabel('Time (UTC)') # x label
    ax.set_ylabel(str(yTuple[0]) + ' (' + yTuple[1] + ')') # y label
    ax.set_title(fName + '\n' + tStrTitle) # title

    fListing = 0
    tFormatDir = timeRecordIndicator(ts1, ts2)

    if fListing == 1:
        tempDir = os.path.join(saveDir, tFormatDir)
        createDir(tempDir)
        saveFileName = yTuple[0] + '-ts-' + tStr
        sDir = os.path.join(tempDir, saveFileName)
    else:
        createDir(saveDir)
        saveFileName = yTuple[0] + '-ts-' + tFormatDir + '-' + tStr
        sDir = os.path.join(saveDir, saveFileName)


    plt.savefig(str(sDir),dpi=int(args.res)) # save figure
    plt.close()
    
def timeRecordIndicator(t0, t1):
    tSec = (t1-t0).total_seconds()
    
    if tSec <= 3600:
        fStr = 'hourly'
    elif (tSec > 3600 and tSec <= 3600*24):
        fStr = 'daily'
    elif (tSec > 3600*24 and tSec <= 3600*24*7):
        fStr = 'weekly'
    elif (tSec > 3600*24*7 and tSec <= 3600*24*7*4):
        fStr = 'monthly'
    elif (tSec > 3600*24*7 and tSec <= 3600*24*7*4):
        fStr = 'yearly'
    else:
        fStr = 'na'
    return fStr

def buildTimes(t0, t1, secs):
    tH = t0 + timedelta(hours=1)
    tD = t0 + timedelta(days=1)
    tW = t0 + timedelta(weeks=1)
    if secs < 3600*24: # less than a day
        hour = rangeTimes(HOURLY, t0, t1)
        timeAry = np.concatenate((hour,record), axis=0)
    elif (secs >= 3600*24 and secs < 3600*24*7):
        hour = rangeTimes(HOURLY, t0, tH) # one hour
        day = rangeTimes(DAILY, t0, tD) 
        timeAry = np.concatenate((hour,day,record), axis=0)
    elif (secs >= 3600*24*7 and secs < 3600*24*7*4):
        hour = rangeTimes(HOURLY, t0, tH)
        day = rangeTimes(DAILY, t0, tD)
        week = rangeTimes(WEEKLY, t0, t1)
        timeAry = np.concatenate((hour,day,week,record), axis=0)
    elif (secs >= 3600*24*7*4):
        hour = rangeTimes(HOURLY, t0, tH)
        day = rangeTimes(DAILY, t0, tD)
        week = rangeTimes(WEEKLY, t0, tW)
        month = rangeTimes(MONTHLY, t0, t1)
        timeAry = np.concatenate((hour,day,week,month,record), axis=0)
    return timeAry
        
def rangeTimes(freq, tS, tE):
    # Function returns a list of times between two datetimes
    # Where freq must be one of YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, or SECONDLY.
    timeList = list(rrule(freq, dtstart=tS, until=tE))
    arr = np.empty((0,2))
    for tStart, tEnd in zip(timeList, timeList[1:]):
        arr = np.append(arr, np.array([[tStart,tEnd]]),0)    
    return arr

def subsampleData(xArray, yArray, t0, t1):
    # This function returns data (x,y) between start time and end time
    # mpl datenum array, y data, start datetime, end datetime
    xTemp = xArray[np.where((xArray>= t0) & (xArray <=t1))]
    yTemp = yArray[np.where((xArray>= t0) & (xArray <=t1))]
    return xTemp, yTemp
    
def createDir(newDir):
    # Check if dir exists.. if it doesn't... create it.
    if not os.path.isdir(newDir):
        try:
            os.makedirs(newDir)
        except OSError:
            if os.path.exists(newDir):
                pass
            else:
                raise

def routine(ncFile):
    global fName
    print ncFile
    head, tail = os.path.split(ncFile)
    fName = tail.split('.', 1)[0]
    createLineSpace()

    print args.saveDir
    print fName
    saveMainDir = os.path.join(args.saveDir, fName)

    createDir(saveMainDir)
    
    try:
        f = nc.Dataset(ncFile) # Open netcdf4 file
    except RuntimeError:
        return
        
    if len(f.groups) == 0:
        print 'No Groups detected.'

        varList = []
        varList = varDict[f.stream] # Get variables we DONT want to look at from pickle file dictionary
        varList.sort() # sort alphabetically

        groupDict = {}
        groupDict['NoGroup'] = varList
    else:
        print 'Groups detected.'
        groups = f.groups
        # print groups
        groupDict = {}
        for test in groups:
            #print test
            grpVars = f.groups[test].groups
            #print grpVars                    
            for grpNum in grpVars:
                #print grpNum
                gVars = f.groups[test].groups[grpNum].variables.keys()
                # print gVars
                varList = []
                
                for varNum in gVars:
                    varList.append(str(varNum))
            
            varList.sort()
            groupDict[str(test)] = varList

    createLineSpace()

    gLib = [s for s in groupDict.keys()]
    gLibUse = gLib

    for dgroups in gLibUse:  	    
        if dgroups == 'NoGroup':  	        
            gData = f
            groupDir = saveMainDir
        else: 
            gData = f.groups[dgroups].groups['1']
            # print gData
            groupName = dgroups[0:23]
            groupName = groupName.replace('|','_')                       
            groupDir = os.path.join(saveMainDir, groupName)

        if args.pltType == 'ts':
            # Ask user for X axis (time)
            xVar = f.variables['time'] # find whatever the time variable is
            try:
                xD = xVar[:]
            except:
                continue
            #print len(xD)
            # print xVar
            xUnits = str(xVar.units)
            xD = nc.num2date(xD, xUnits) # nc time to datetime
            t0 = min(xD)
            t1 = max(xD) # get time min and max
            global record
            record = np.array([[t0,t1]])

            reg_ex = re.compile('|'.join(groupDict[dgroups]))
            yVars = [s for s in f.variables.keys() if not reg_ex.search(s)]

            reg_ex = re.compile('|'.join(['provenance', 'qc', 'id', 'obs', 'deployment', 'volts', 'counts']))

            yVars = [s for s in yVars if not reg_ex.search(s)]
            # yVars = [s for s in groupDict[dgroups] if not 'time' in s]

            print 'Plotting Vars:'
            print yVars

            createLineSpace()
        
            for var in yVars: # iterate through y variable dictionary
                # print var
                try:
                    yD = gData.variables[var][:] # load variable data
                except:
                    continue

                # if len(np.unique(yD)) == 1:
                #     print "One value. Continuing"
                #     continue
            
                if isinstance(yD[0], basestring): # check if array of strings
                    continue # skip if the array contains strings
                elif yD[0].dtype == 'S1':
                    continue
                else:
                    try:
                        yU = str(gData.variables[var].units)
                    except AttributeError:
                        yU = 'n/a'
                        pass
                    yI = (var, yU, var) # name, unit, name
                    secs = (t1-t0).total_seconds()
                    # yMa = np.ma.masked_outside(yD, yD.mean() - 50*yD.std(), yD.mean() + 50*yD.std())
                    yMa = np.ma.masked_where(yD==-9999999, yD)

                    if len(yMa) == 0:
                        continue
                    yMin = np.nanmin(yMa); yMax = np.nanmax(yMa)
                    
                    yI = yI + (yMin,yMax,)

                    timeAry = buildTimes(t0, t1, secs)

                    for t in timeAry:
                        xT, yT = subsampleData(xD, yMa, t[0], t[1])


                        if len(xT) == 0:
                            continue
                        elif len(yT) == 0:
                            continue
                        elif np.ma.count_masked(yT) == len(yT):
                            continue
                        else:
                            plotTimeSeries(xT, yT, yI, groupDir)

def main():
    # script usage message
    USAGE = """
    netCDF Plotting Script.
    
    Use this script to recursively search a directory and plot variables for each netCDF file. This is a generic plotting routine that can plot time series, depth profiles, and x-y plots
    """
    argParser = argparse.ArgumentParser(description=USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # Add options:
    argParser.add_argument('-s', '--save',
        action='store',
        default=os.getcwd(),
        help='Directory to save plots. Defaults to current working directory.',
        dest='saveDir')

    argParser.add_argument('-u', '--url',
        action = 'store',
        default = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/catalog/ooiufs01/catalog.xml',
        help = 'TDS catalog - must end in .xml. Defaults to http://opendap-devel.ooi.rutgers.edu:8090/thredds/catalog/ooiufs01/catalog.xml',
        dest = 'url')

    argParser.add_argument('-p', '--plotType',
        action='store',
        default = 'ts',
        help='Plot Type: Timeseries = ts, Profile = pr, or Line Chart = lc',
        dest='pltType')
        
    argParser.add_argument('-r', '--resolution',
        action='store',
        default=100,
        help='Resolution in dots per inch. Default 100',
        dest='res')
    
    argParser.add_argument('-tsM', '--linestyle',
        default='-ro',
        action='store',
        help='Control the line style or marker. Refer to http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot for accepted controls.',
        dest='lineStyle')

    argParser.add_argument('-la', '--lockaxes',
        action='store',
        default=True,
        dest='lock',
        help='Make the y-axes equal for single variables over an extended period of time')


    # argParser.add_argument('-')
    global args
    args = argParser.parse_args()
    
    # print "Opendap url for netCDF4 files: " + args.url
    print "Directory to save plots:" + args.saveDir
    print args.url

    #url='http://opendap-devel.ooi.rutgers.edu:8090/thredds/catalog/ooiufs01/catalog.xml'
    opendap = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/'
    pkl_url = 'https://raw.githubusercontent.com/ooi-data-review/ooi-parameters-dict/master/ooi_nonscience_parameters.pkl'

    url = args.url
    assert isinstance(url, object)
    arrayOOI = iterate_items(url)
    ncmlList = []

    print "Sensors: Codes"
    print "----------------------------------------"
    print "Conductivity, Temperature, Density: CTD"
    print "Dissolved Oxygen: DO"
    print "Fluorometry (chl-a,cdom,backscatter): FLOR"
    print "Photosynthetically Active Radiation: PAR"
    print "Nitrate: NUTNR"
    print "Meteorological Data: METBK"
    print "----------------------------------------"
    # print "Acoustic Doppler current profiler: ADCP"
    # print "HYD"
    # print "OPTAA"
    # print "RASFL"
    # print "PCO2"
    # print "PH"
    # print "PRESF"
    # print "SPKIR"
    # print "VEL3D"
    # print "VELPT"
    # print "WAVSS"
    # print "ZPLSC"
    # print "FDCHP"
    # print "FLCDR"
    # print "FLNTU"

    sI = raw_input("Enter list of sensors codes (comma-separated, all caps): ")
    sI = sI.split(',')
    reX = re.compile('|'.join(sI))
    selectedArrays = getMultipleVariables(arrayOOI)

    print "Arrays Selected"
    print ' '
    print ' '

    # load pickle file. This contains a python dictionary containing streams and relevant science variables
    pkl_file = urllib2.urlopen(pkl_url)
    # file = open(pkl_file, 'rb')
    global varDict
    varDict = pickle.load(pkl_file)
    pkl_file.close()
    # file.close()

    for urls in selectedArrays:
        platformOOI = iterate_items(urls)
        selectedStreams = getMultipleVariables(platformOOI)
        for platforms in selectedStreams:
            instrumentOOI = iterate_items(platforms)
            instrumentOOISel = [s for s in instrumentOOI if reX.search(s)]
            for instruments in instrumentOOISel:
                deliveryMTD = iterate_items(instruments)
                for methods in deliveryMTD:
                    streams = iterate_items(methods)
                    for stream in streams:
                        (root, ext) = os.path.splitext(stream)
                        streamURL = root + '.html'
                        dataset = iterate_data(stream)
                        ncml = [s for s in dataset if '.ncml' in s]
                        ncmlList.append(opendap + ncml[0])

    for ncmls in ncmlList:
        if not 'metadata' in ncmls:
            if not 'calibration' in ncmls:
                if not 'eng' in ncmls:
                    print ncmls
                    routine(ncmls)
            
if __name__ == '__main__':
    main()
