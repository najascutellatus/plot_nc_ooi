import os,sys,time
import netCDF4 as nc
import numpy as np
import pylab
from datetime import datetime, timedelta
import matplotlib.pyplot as plt 
import matplotlib.dates as mDate
import matplotlib.ticker as ticker
import pytz
from dateutil.rrule import *
'''
This script is used to generates plots from any netcdf file containing a time 
variable and containing other data.

You can create time series, depth profiles, and regular line plots
'''

################################################################################
# Functions 
################################################################################

def createLineSpace():
    print ".\n..\n...\n....\n...\n..\n.\n"

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

def getFileName(dirStr):
    dirStr = dirStr[dirStr.rfind('/')+1:dirStr.rfind('.')]
    return dirStr

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
                break #once the variable is selected break out of the loop
    return singleVarName
    
def getMultipleVariables(library):
    multiVarLib = [] # Create empty list for y variables and metadata
    for variable in library:
        var = str(raw_input("Variable: %s"%variable + " <n> : ")) or 'n'
        if var == 'y':
            multiVarLib.append(variable)
    return multiVarLib

def plotTimeSeries(x, y, yTuple, saveDir):
    ## function to create time series plot
    ## x: array of datetimes, x: data to plot
    ## yTuple: ('variable name', 'units'), saveDir
    x = mDate.date2num(x) # convert datetime to matplotlib time
    yMa = np.ma.masked_outside(y, y.mean() - 2*y.std(), y.mean() + 2*y.std())
    ymin = np.min(yMa)
    ymax = np.max(yMa)
    nMa = np.ma.count_masked(yMa)
      
    fig,ax = plt.subplots()
    minorLocator = ticker.AutoMinorLocator()

    ax.plot_date(x, yMa, xdate=True, ydate=False, tz=pytz.utc,
    color='black', linestyle='-', linewidth=.5,
    marker='o', markersize=4, markerfacecolor='red', markeredgecolor='black')
    
    # Image size
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 8.5
    plt.rcParams["figure.figsize"] = fig_size
    
    # setup axes
    plt.ylim((yTuple[3], yTuple[4]))
    ax.xaxis.set_minor_locator(minorLocator)
    xax = ax.get_xaxis().get_major_formatter()

    xax.scaled = {
        365.0 : '%Y-M', # data longer than a year
        30.   : '%Y-m\n%d', # set the > 1m < 1Y scale to Y-m
        1.0   : '%b-%d\n%H:%M', # set the > 1d < 1m scale to Y-m-d
        1./24.: '%b-%d\n%H:%M', # set the < 1d scale to H:M
        1./48.: '%b-%d\n%H:%M:%S',
    }
    
    y_formatter = ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)
    # plt.setp(xax.get_majorticklabels(), rotation=50)
    plt.grid()
    
    # setup labels and title
    ax.legend(["Maximum: %f" % ymax 
    + "\nMinimum: %f" % ymin 
    + "\nMean: %f" % np.mean(yMa) 
    + "\n# Masked (+/-  2 stdev): %d " % nMa], loc='best')
    ax.set_xlabel('Time (UTC)') # x label
    ax.set_ylabel(str(yTuple[0]) + ' (' + yTuple[1] + ')') # y label
    ax.set_title(fName) # title

    ts1 = min(x)
    ts2 = max(x)
    ts1 = mDate.num2date(ts1)
    ts2 = mDate.num2date(ts2)
    tStr = ts1.strftime('%Y-%m-%dT%H%M%S') + '_' + ts2.strftime('%Y-%m-%dT%H%M%S') 
    
    fListing = 0
    tFormatDir = timeRecordIndicator(ts1, ts2)
    
    if fListing == 1:
        tempDir = os.path.join(saveDir, tFormatDir)
        createDir(tempDir)
        saveFileName = fName + '-' + yTuple[0] + '-timeseries-' + tFormatDir + '-' + tStr  
        sDir = os.path.join(tempDir, saveFileName)
    else:
        createDir(saveDir)
        saveFileName = fName + '-' + yTuple[0] + '-timeseries-' + tFormatDir + '-' + tStr  
        sDir = os.path.join(saveDir, saveFileName)
        
        
    plt.savefig(str(sDir),dpi=100) # save figure
    plt.close()
    
def timeRecordIndicator(t0, t1):
    tSec = (t1-t0).total_seconds()
    
    if (tSec <= 3600):
        fStr = 'hourly'
    elif (tSec > 3600 and tSec <= 3600*24):
        fStr = 'daily'
    elif (tSec > 3600*24 and tSec <= 3600*24*7):
        fStr = 'weekly'
    elif (tSec > 3600*24*7 and tSec <= 3600*24*7*4):
        fStr = 'monthly'
    return fStr

def buildTimes(t0, t1, secs):
    tH = t0 + timedelta(hours=2)
    tD = t0 + timedelta(days=1)
    if secs < 3600*24: # less than a day
        hour = rangeTimes(HOURLY, t0, tH)
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
        week = rangeTimes(WEEKLY, t0, t1)
        month = rangeTimes(MONTHLY, t0, t1)
        timeAry = np.concatenate((hour,day,week,month,record), axis=0)
    return timeAry
        
def rangeTimes(freq, tS, tE):
    # Function returns a list of times between two datetimes
    # Where freq must be one of YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, or SECONDLY.
    timeList = list(rrule(freq, dtstart=tS, until=tE))
#    timeList.append(tE)
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
####################################################################

# ncFile = '/Users/michaesm/Documents/MATLAB/CP05G004_GL004_03-CTDGVM000_telemetered_ctdgv_m_glider_instrument_2014-10-06T235844Z-2014-10-20T235844Z.nc'
#Group 1b
ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group1B/ctdbp_no/ctdbp_no_sample_L1.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group1B/ctdpf_sbe43/ctdpf_sbe43_sample_L1.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group1B/thsph/thsph_sample_L1.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group1B/velpt/velpt_velocity_data_L1.nc'

#Group2A
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/ctdpf_sbe43/ctdpf_sbe43_sample.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/nutnr/nutnr_a_sample_L1.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/trhph/trhph_sample_L1.nc'

#Group 3
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/optaa/optaa_sample_L1.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/prest/prest_real_time_L1.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/spikr/spkir_data_record_L1.nc'
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/tmpsf/tmpsf_sample_L0.nc'

#Group 4
# ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/ctdpf_optode/ctdpf_optode_sample_L1.nc'

fName = getFileName(ncFile)
createLineSpace()
saveDir = str(raw_input("Select save directory <Enter for %s>: "%os.getcwd())) or os.getcwd()
saveMainDir = os.path.join(saveDir, fName)

createDir(saveMainDir)
            
f = nc.Dataset(ncFile) # Open netcdf4 file

if len(f.groups) == 0:
    print 'No Groups detected.'
    variables = f.variables.keys() # Get list if variables
    
    # create dict of group
    varList = []
    for varNum in variables: # iterate through variables to clean up string
        varList.append(str(varNum))

    varList.sort() # sort alphabetically
    groupDict = {}
    groupDict['NoGroup'] = varList
else:
    print 'Groups detected.'
    groups = f.groups
    groupDict = {}
    groupLib = []
    for group in groups:
        print group
        gVars = f.groups[group].variables.keys()
        varList = []
        for varNum in gVars:
            varList.append(str(varNum))
        varList.sort()
        groupDict[str(group)] = varList

# Prompt user for the type of plot they would like to create
pltType = definePlot()
createLineSpace()

print "Choose group(s) you want to grab data from."
print "Pressing <Enter> inputs 'n' as a default   "
    
for gName in groupDict.keys():
    print gName + ": " + str(groupDict[gName]) + "\n"

gLib = [s for s in groupDict.keys()]

gLibUse = getMultipleVariables(gLib)

for groups in gLibUse:
    if groups == 'NoGroup':
        gData = f
        groupDir = saveMainDir
    else:
        gData = f.groups[groups]
        groupDir = os.path.join(saveMainDir, groups)
    
    if pltType == 'timeseries':
        # Ask user for X axis (time)
        xVar = f.variables['time'] # create seperate time variable
        xD = xVar[:]
        xUnits = str(xVar.units)
        xD = nc.num2date(xD, xUnits) # nc time to datetime
        t0 = min(xD)
        t1 = max(xD) # get time min and max
        record = np.array([[t0,t1]])

        #Ask user for Y axis (sensor)
        print "****************************************************************"
        print "Please choose sensor (y-axis) variable(s). (y/n)                "
        print "Pressing <Enter> inputs 'n' as a default                        "
        print "****************************************************************"
        yVars = [s for s in groupDict[groups] if not 'time' in s]
        
        createLineSpace()
        
        for var in yVars: # iterate through y variable dictionary
            print var
            # print gData.variables
            yD = gData.variables[var][:] # load variable data
            
            if len(np.unique(yD)) == 1:
                print "One value. Continuing"
                continue
            
            if isinstance(yD[0], basestring): # check if array of strings
                continue # skip if the array contains strings
            else:
                try:
                    yU = str(gData.variables[var].units)
                except AttributeError:
                    yU = 'n/a'
                    pass
                yI = (var, yU, var) # name, unit, name
                secs = (t1-t0).total_seconds()
                yMa = np.ma.masked_outside(yD, yD.mean() - 2*yD.std(), yD.mean() + 2*yD.std())
                yMin = np.min(yMa)
                yMax = np.max(yMa)
                yI = yI + (yMin,yMax,)

                timeAry = buildTimes(t0, t1, secs)

                for t in timeAry:
                    xT, yT = subsampleData(xD, yD, t[0], t[1])
                    
                    if len(xT) == 0:
                        continue
                    else:
                        plotTimeSeries(xT, yT, yI, groupDir)

# elif pltType == 'profile':
#     # print "******************************************************"
#     # print "Choose time (x-axis) variable. (y/n)                  "
#     # print "Pressing <Enter> inputs 'no' as default               "
#     # print "******************************************************"
#     # timeVarLib = [s for s in varLib if 'time' in s]
#     # xVarName = getSingleVariable(timeVarLib)
#     # createLineSpace()
#     xVarName = 'time' # always use the default nc time variable
#     xVar = f.variables[xVarName][:] # assign data to variable
#     xVar = netCDF4.num2date(xVar, str(f.variables[xVarName].units) # convert nc time to datetime
#     t0, t1 = minmax(xVar)
#     xVar = mDate.date2num(xVar) # convert datetime to matplotlib time
#
#     #Ask user for Y axis (sensor)
#     print "********************************************************************"
#     print "Choose correct pressure/depth variable. (y/n)                       "
#     print "Pressing <Enter> inputs 'n' as a default                            "
#     print "********************************************************************"
#     yVarLib = [s for s in varLib if 'pressure' in s or 'depth' in s]
#     yVarName = getSingleVariable(yVarLib)
#
#     createLineSpace()
#
#     print "********************************************************************"
#     print "Please select sensor to display. (yes/no)                           "
#     print "Multiple plots will be created if more than one variable is selected"
#     print "Pressing <Enter> inputs 'no' as default                             "
#     print "********************************************************************"
#     zVarLibTimeRemoved = [s for s in varLib if not 'time' in s or 'depth' in s or 'pressure' in s]
#     zVarLibTimeRemoved.remove(yVarName)
#     zVarDict = getMultipleVariables(zVarLibTimeRemoved)
#     createLineSpace()
#
#     #Get info on x and y variables
#
#     yVarDict = {}
#     yVarDict[yVarName] = str(f.variables[yVarName].units)
#     yVar = f.variables[yVarName][:] # assign data to variable
#     yVarFill = f.variables[yVarName]._FillValue # get fill value
#     yVar = np.ma.masked_where(yVar == yVarFill, yVar) # mask fill value
#
#     if yVarDict[yVarName] == 'bar':
#         yVar = yVar * 10
#         print "Converting to decibars"
#         yVarDict[yVarName] = 'decibar'
#
#     createLineSpace()
#     print "Plotting the following:"
#     print "Variable Name: ['units', 'name', 'FillValue']"
#     for key in zVarDict:
#         print "'"+key+"':" + str(zVarDict[key])
#
#     keys = zVarDict.keys()
#     keys.sort()
#
#     for key in zVarDict: # iterate through y variable dictionary
#         zVarName = key # get name of variable
#         zVarUnit = zVarDict[key][0] # get units of variable
#         zVarLongName = zVarDict[key][1] # get long name of variable
#         zVarFillValue = float(zVarDict[key][2]) # get fill value of variable
#         zVar = f.variables[zVarName][:] # load variable data
#         zVar_ma = np.ma.masked_where(zVar <  0.2 , zVar) # mask zero values for y variable
#
#         days = mDate.AutoDateLocator()
#         fmt = mDate.DateFormatter('%m/%d')
#
#         fig,ax = plt.subplots()
#         sFig = ax.scatter(xVar, yVar, s=10, c= zVar_ma)
#         plt.setp(sFig, 'edgecolors', 'None')
#
#         # setup colorbar
#         cbar = plt.colorbar(sFig)
#         cbar.ax.set_ylabel(str(zVarName) + ' (' + zVarDict[zVarName][0] + ')')
#         # cbar.add_lines(sFig)
#
#         # format axes
#         ax.xaxis.set_major_locator(days)
#         ax.xaxis.set_major_formatter(fmt)
#         fig.gca().invert_yaxis()
#         plt.axis('tight')
#         plt.grid()
#
#
#         # Set plot labels and title
#         ax.set_xlabel('Time (UTC)') # x label
#         ax.set_ylabel(str(yVarName) + ' (' + yVarDict[yVarName] + ')') # y label
#         ax.set_title(fName) # title
#
#         # save figure
#         plt.savefig(saveFile+'_'+zVarName+'_profile',dpi=120) # save figure
#         # mlab.pyplot.show()
# elif pltType == 'line'
#     # Ask user for X axis (time)
#     print "******************************************************"
#     print "Please choose time (x-axis) variable. (y/n)           "
#     print "Pressing <Enter> inputs 'no' as default               "
#     print "******************************************************"
#     xVarName = getSingleVariable(varLib)
#     createLineSpace()
#
#     #Ask user for Y axis (sensor)
#     print "********************************************************************"
#     print "Please choose sensor (y-axis) variable(s). (y/n)                    "
#     print "Pressing <Enter> inputs 'n' as a default                            "
#     print "********************************************************************"
#     yVarDict = getMultipleVariables(varLib)
#     createLineSpace()
#
#     #Get info on x and y variables
#     xVarDict = {} # Create empty dictionary for y variables and time units
#     xVarDict[xVarName] = str(f.variables[xVarName].units)
#     xVar = f.variables[xVarName][:]
#     xVar = netCDF4.num2date(xVar, xVarDict[xVarName]) # convert nc time to datetime
#     xVar = mDate.date2num(xVar) # convert datetime to matplotlib time
#
#     print "Plotting the following:"
#     print "Variable Name: ['units', 'name', 'FillValue']"
#
#     for key in yVarDict:
#         print "'"+key+"':" + str(yVarDict[key])
#
#     keys = yVarDict.keys()
#     keys.sort()
#
#     for key in yVarDict: # iterate through y variable dictionary
#         yVarName = key # get name of variable
#         yVarUnit = yVarDict[key][0] # get units of variable
#         yVarLongName = yVarDict[key][1] # get long name of variable
#         yVarFillValue = float(yVarDict[key][2]) # get fill value of variable
#         yVar = f.variables[yVarName][:] # load variable data
#
#         yVar_ma = np.ma.masked_where(yVar ==  0 , yVar) # mask zero values for y variable
#
#         days = mDate.DayLocator()
#         fmt=mDate.DateFormatter('%m/%d')
#
#         fig,ax = plt.subplots()
#
#         ax.plot_date(xVar, yVar_ma, 'k-', xdate=True, ydate=False, tz=pytz.utc)
#
#         # setup axes
#         ax.xaxis.set_major_locator(days)
#         ax.xaxis.set_major_formatter(fmt)
#         plt.grid()
#
#         # setup labels and title
#         ax.set_xlabel('Time (UTC)') # x label
#         ax.set_ylabel(str(yVarName) + ' (' + yVarDict[yVarName][0] + ')') # y label
#         ax.set_title(fName) # title
#
#         plt.savefig(saveFile+'_'+yVarName+'_line',dpi=120) # save figure
#         # mlab.pyplot.show()
#
