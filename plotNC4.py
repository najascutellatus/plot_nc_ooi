import os,sys,time
import netCDF4
import numpy as np
import pylab,datetime
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
# Helper Functions 
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
    pltType = raw_input("Enter number (Enter <1>): ") or '1'
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
    yMa = np.ma.masked_outside(y, y.mean() - 50*y.std(), y.mean() + 50*y.std())
    ymin = np.min(yMa)
    ymax = np.max(yMa)
    nMa = np.ma.count_masked(yMa)
    # print nMa
      
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
    ax.xaxis.set_minor_locator(minorLocator)
    xax = ax.get_xaxis().get_major_formatter()

    xax.scaled = {
        365.0 : '%Y', # data longer than a year
        30.   : '%Y-m\n%d', # set the > 1m < 1Y scale to Y-m
        1.0   : '%b-%d\n%H:%M', # set the > 1d < 1m scale to Y-m-d
        1./24.: '%b-%d\n%H:%M', # set the < 1d scale to H:M
        1./48.: '%H:%M:%S',
    }
    
    y_formatter = ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)
    # plt.setp(xax.get_majorticklabels(), rotation=50)
    plt.grid()
    
    # setup labels and title
    
    ax.legend(["Maximum: %f" % ymax 
    + "\nMinimum: %f" % ymin 
    + "\nMean: %f" % np.mean(yMa) 
    + "\n# Masked (+/- 50stdev): %d " % nMa], loc='best')
    ax.set_xlabel('Time (UTC)') # x label
    ax.set_ylabel(str(yTuple[0]) + ' (' + yTuple[1] + ')') # y label
    ax.set_title(fName) # title

    ts1, ts2 = minmax(x)
    ts1 = mDate.num2date(ts1)
    ts2 = mDate.num2date(ts2)
    tStr = ts1.strftime('%Y-%m-%dT%H%M%S') 
    + '_' + ts2.strftime('%Y-%m-%dT%H%M%S') 
    folderType = saveSubDir(ts1, ts2)
    tempDir = os.path.join(saveDir, folderType)
    createDir(tempDir)
    saveFileName = fName + '-' + yTuple[0] + '-timeseries-' + tStr  
    sDir = os.path.join(tempDir, saveFileName)
    
    plt.savefig(sDir,dpi=100) # save figure
    plt.close()
    
def saveSubDir(t0, t1):
    tSec = (t1-t0).total_seconds()
    
    if (tSec < 3600*24*7):
        fStr = 'daily'
    elif (tSec >= 3600*24*7 and tSec < 3600*24*7*4):
        fStr = 'weekly'
    elif (tSec > 3600*24*7*4):
        fStr = 'monthly'
    return fStr
    
def returnTimeFrequencies(freq, t0, t1):
    # Function returns a list of times between two datetimes
    # Where freq must be one of YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, or SECONDLY.
    timeList = list(rrule(freq, dtstart=t0, until=t1))
    timeList.append(t1)
    arr = np.empty((0,2))
    for tStart, tEnd in zip(timeList, timeList[1:]):
        arr = np.append(arr, np.array([[tStart,tEnd]]),0)    
    return arr

def returnDataBetweenTimes(xArray, yArray, t0, t1):
    # This function returns data (x,y) between start time and end time
    # mpl datenum array, y data, start datetime, end datetime
    #t0 = mDate.date2num(t0)
    #t1 = mDate.date2num(t1)
    xTemp = xArray[np.where((xArray>= t0) & (xArray <=t1))]
    yTemp = yArray[np.where((xArray>= t0) & (xArray <=t1))]
    return xTemp, yTemp

def minmax(thisList):
    t0 = min(thisList)
    t1 = max(thisList)
    return t0, t1
    
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
####################################################################
####################################################################

#ncFile = '/Users/michaesm/Documents/MATLAB/CP05G004_GL004_03-CTDGVM000_telemetered_ctdgv_m_glider_instrument_2014-10-06T235844Z-2014-10-20T235844Z'
ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group2A3/tmpsf/tmpsf_sample_L0.nc'
fName = getFileName(ncFile)
createLineSpace()
saveDir = str(raw_input("Select save directory <Enter for %s>: "%os.getcwd())) or os.getcwd()
saveMainDir = os.path.join(saveDir, fName)

createDir(saveMainDir)
            
f = netCDF4.Dataset(ncFile) # Open netcdf4 file

if len(f.groups) == 0:
    print 'No Groups detected.'
    variables = f.variables.keys() # Get list if variables
    
    # create dict of group
    varList = []
    for varNum in variables: # iterate through variables to clean up string
        varList.append(str(varNum))

        # varList += "'" + str(varNum) + "',"

    varList.sort() # sort alphabetically
    groupDict = {}
    groupDict['NoGroup'] = str(varList)
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

for gName in groupDict.keys():
    # print "Choose group(s) you want to grab data from."
    # print "Pressing <Enter> inputs 'n' as a default   "
    print gName + ": " + str(groupDict[gName]) + "\n"

gLib = [s for s in groupDict.keys()]

gLibUse = getMultipleVariables(gLib)

for groups in gLibUse:
    gData = f.groups[groups]
    groupDir = os.path.join(saveMainDir, groups)
    
    
    if pltType == 'timeseries':
        # Ask user for X axis (time)
        xVar = f.variables['time'] # create seperate time variable
        xVarData = xVar[:]
        
        xVarData = netCDF4.num2date(xVarData, str(xVar.units)) # convert nc time to datetime
        t0, t1 = minmax(xVarData) # get time min and max
        record = np.array([[t0,t1]])
#        xVarData = mDate.date2num(xVarData)
        #Ask user for Y axis (sensor)
        print "********************************************************************"
        print "Please choose sensor (y-axis) variable(s). (y/n)                    "
        print "Pressing <Enter> inputs 'n' as a default                            "
        print "********************************************************************"
        yVarLib = [s for s in groupDict[groups] if not 'time' in s]
        yVarUse = yVarLib
#        yVarUse = getMultipleVariables(yVarLib)
        
        createLineSpace()
#        keys = yVarDict.keys() # Get dictionary key names
#        keys.sort()
        
        for var in yVarUse: # iterate through y variable dictionary
            yTuple = (var, gData.variables[var].units, var)#, float(gData[var].fill_value))
            # name, unit, long name, fill
            yVarData = gData.variables[var][:] # load variable data
            seconds = (t1-t0).total_seconds()
            
            if seconds < 3600*24: # less than a day
                daily = returnTimeFrequencies(DAILY, t0, t1)
                timeArray = np.concatenate((record,daily), axis=0)
            elif (seconds >= 3600*24 and seconds < 3600*24*7):
                daily = returnTimeFrequencies(DAILY, t0, t1)
                timeArray = np.concatenate((record, daily), axis=0)
            elif (seconds >= 3600*24*7 and seconds < 3600*24*7*4):
                daily = returnTimeFrequencies(DAILY, t0, t1)
                weekly = returnTimeFrequencies(WEEKLY, t0, t1)
                timeArray = np.concatenate((record,daily, weekly), axis=0)
            elif (seconds >= 3600*24*7*4):
                daily = returnTimeFrequencies(DAILY, t0, t1)
                weekly = returnTimeFrequencies(WEEKLY, t0, t1)
                monthly = returnTimeFrequencies(MONTHLY, t0, t1)
                timeArray = np.concatenate((record,daily,weekly,monthly), axis=0)    
    
            for times in timeArray:
                xTemp, yTemp = returnDataBetweenTimes(xVarData, yVarData, times[0], times[1])
                plotTimeSeries(xTemp, yTemp, yTuple, groupDir) 

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
