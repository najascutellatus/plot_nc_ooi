#!/usr/bin/python
import os,sys,time
import numpy as np
import netCDF4
#import netCDF3
import pylab,datetime
import matplotlib as mlab
import matplotlib.pyplot as plt
import numpy as np



ncfile='/Users/michaesm/Documents/repositories/ooi-tools/plot-nc-ooi/adcpplot/mullica_adp_NJTPA.nc'

print ncfile
nc = netCDF4.Dataset(ncfile,'r')
print nc

rt=np.array(mlab.dates.date2num(datetime.datetime(2006,1,1,0,0,0)))
nts=-2016*8
time=nc.variables['time'][nts:]
p=nc.variables['pressure'][nts:]
u=np.transpose(nc.variables['u'][nts:,:])
v=np.transpose(nc.variables['v'][nts:,:])
bins=nc.variables['bins'][:]
nc.close()
time=time+rt
ang=-16.4
ru=u*np.cos(ang*np.pi/180.0)-v*np.sin(ang*np.pi/180.0)
rv=v*np.cos(ang*np.pi/180.0)+u*np.sin(ang*np.pi/180.0)

fmt=mlab.dates.DateFormatter('%m/%d')
days = mlab.dates.DayLocator() 
#
#fig=mlab.pyplot.figure()
#ax=fig.add_axes([0.1,0.1,0.8,0.8])
ax=mlab.pyplot.subplot(2, 1, 1)
pc=ax.pcolor(time,bins,rv)
ax.plot(time,p,'k')
pc.set_clim([-75, 75])
ax.set_ylim([0.4,9])
ax.set_xlim([time.min(),time.max()])
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(fmt)
ax.set_title('Mullica River Along Channel Velocity (cm/s)')
ax.set_ylabel('Bin Range (m)')
mlab.pyplot.colorbar(pc)
#plt.pcolor(time,bins,u)

ax=mlab.pyplot.subplot(2, 1,2)
pc=ax.pcolor(time,bins,ru)
ax.plot(time,p,'k')
pc.set_clim([-75, 75])
ax.set_ylim([0.4,9])
ax.set_xlim([time.min(),time.max()])
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(fmt)
ax.set_title('Mullica River Cross Channel Velocity (cm/s)')
ax.set_ylabel('Bin Range (m)')
mlab.pyplot.colorbar(pc)



plt.show()


