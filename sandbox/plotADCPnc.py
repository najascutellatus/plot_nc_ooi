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


ncFile = '/Users/michaesm/Documents/projects/ooi/rsn_data/Group1B/adcps/adcp_pd0_beam_parsed_L1.nc'

f = nc.Dataset(ncFile)

time = f.variables['time']

timeData = time[:]
timeUnits = str(time.units)

xD = nc.num2date(timeData, timeUnits)
