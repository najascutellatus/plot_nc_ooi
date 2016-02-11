#! /usr/local/bin/python
import os, sys, time
import netCDF4
import pylab, datetime
import matplotlib as mlab
import matplotlib.pyplot as plt
import numpy as np



# ncfile='/Users/michaesm/Documents/repositories/ooi-tools/plot-nc-ooi/adcpplot/mullica_adp_NJTPA.nc'
ncfile = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/ufs-west/Coastal_Pioneer/CP05MOAS/01-ADCPAM000/recovered_host/CP05MOAS-GL388-01-ADCPAM000-adcp_velocity_glider-recovered_host/CP05MOAS-GL388-01-ADCPAM000-recovered_host-adcp_velocity_glider-20141109T004210-20141109T234428.nc'

print ncfile
nc = netCDF4.Dataset(ncfile,'r')
print nc

# rt=np.array(mlab.dates.date2num(datetime.datetime(1900,1,1,0,0,0)))
# nts=-2016*8
time = netCDF4.num2date(nc.variables['time'][:], 'seconds since 1900-01-01 00:00:00')

# p=nc.variables['pressure'][:]
u = nc.variables['eastward_seawater_velocity'][:]
v = nc.variables['northward_seawater_velocity'][:]
time = np.resize(time, u.shape)

bins = nc.variables['bin_depths'][:]
nc.close()

# time=time+rt

# ang=-16.4
# ru=u*np.cos(ang*np.pi/180.0)-v*np.sin(ang*np.pi/180.0)
# rv=v*np.cos(ang*np.pi/180.0)+u*np.sin(ang*np.pi/180.0)

fmt=mlab.dates.DateFormatter('%m/%d')
days = mlab.dates.DayLocator() 
#
#fig=mlab.pyplot.figure()
#ax=fig.add_axes([0.1,0.1,0.8,0.8])
ax=mlab.pyplot.subplot(2, 1, 1)
pc=ax.pcolor(time,bins,v)
# ax.plot(time,p,'k')
pc.set_clim([-75, 75])
ax.set_ylim([0.4,9])
ax.set_xlim([time.min(),time.max()])
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(fmt)
ax.set_title('v (cm/s)')
ax.set_ylabel('Bin Range (m)')
mlab.pyplot.colorbar(pc)
#plt.pcolor(time,bins,u)

ax=mlab.pyplot.subplot(2, 1,2)
pc=ax.pcolor(time,bins,u)
# ax.plot(time,p,'k')
pc.set_clim([-75, 75])
ax.set_ylim([0.4,9])
ax.set_xlim([time.min(),time.max()])
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(fmt)
ax.set_title('u (cm/s)')
ax.set_ylabel('Bin Range (m)')
mlab.pyplot.colorbar(pc)



plt.show()


