#! /usr/local/bin/python

import numpy as np
import scipy as sp
import netCDF4 as nc
import matplotlib.pyplot as plt
import datetime

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



# ctd='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/03-CTDGVM000/recovered_host/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host/CP05MOAS-GL387-03-CTDGVM000-ctdgv_m_glider_instrument_recovered-recovered_host.ncml'
# dost='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/04-DOSTAM000/recovered_host/CP05MOAS-GL387-04-DOSTAM000-dosta_abcdjm_glider_recovered-recovered_host/CP05MOAS-GL387-04-DOSTAM000-dosta_abcdjm_glider_recovered-recovered_host.ncml'
# dost='http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/production/Coastal_Pioneer/CP05MOAS/02-FLORTM000/recovered_host/CP05MOAS-GL387-02-FLORTM000-flort_m_glider_recovered-recovered_host/CP05MOAS-GL387-02-FLORTM000-flort_m_glider_recovered-recovered_host.ncml'

ctd=''


ctdF = nc.Dataset(ctd)
dostF = nc.Dataset(dost)

# grab ctd/dosta time variables
timeC = ctdF.variables['time']
timeD = dostF.variables['time']

sT = nc.date2num(datetime.datetime(2015, 2, 18, 0, 0, 0), timeC.units)
eT = nc.date2num(datetime.datetime(2015, 2, 25, 0, 0, 0), timeC.units)

timeCind = np.where((timeC[:]> sT)&(timeC[:] < eT))
timeDind = np.where((timeD[:]> sT)&(timeD[:] < eT))

# grab the rest of  variables
tCtd = timeC[timeCind]
pCtd = ctdF.variables['sci_water_pressure'][timeCind]

tDo = timeD[timeDind]
ipDost = dostF.variables['int_ctd_pressure'][timeDind]
cpDost = dostF.variables['sci_water_pressure'][timeDind]

tI = interpolate_list(tDo, tCtd, pCtd)

timeCTD = nc.num2date(tCtd, timeC.units)
timeDO = nc.num2date(tDo, timeD.units)

print 'CTD Time Points: ' + str(np.count_nonzero(~np.isnan(tCtd)))
print 'DO Time Points: ' + str(np.count_nonzero(~np.isnan(tDo)))
print 'CTD sci_water_pressure Points: ' + str(np.count_nonzero(~np.isnan(pCtd)))
print 'DO int_ctd_pressure Points (from files): ' + str(np.count_nonzero(~np.isnan(ipDost)))
print 'DO sci_water_pressure Points: ' + str(np.count_nonzero(~np.isnan(cpDost)))
print 'Using the scipy.interpolate function in calc.py (stream_engine): ' + str(np.count_nonzero(~np.isnan(tI)))
# f, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)
# ax1.plot(timeCTD, pCtd, 'k-o')
# ax2.plot(timeDO, ipDost, 'r-o')
# ax3.plot(timeDO, cpDost, 'g-o')
# ax4.plot(timeDO, tI, 'c-o')

# f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
# ax1.plot(timeCTD, pCtd, 'k-o')
# ax2.plot(timeDO, ipDost, 'r-o')
# ax3.plot(timeDO, tI, 'c-o')



