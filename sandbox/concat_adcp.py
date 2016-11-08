
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

# make sure you have dask installed 
# http://xarray.pydata.org/en/latest/io.html#combining-multiple-files
# http://dask.pydata.org/en/latest/

# point this function to the folder containing the .nc files you want to open
ds = xr.open_mfdataset('./*.nc')

# dimension the data along time instead of observations
ds = ds.swap_dims({'obs': 'time'})

# print ds to find the the variable names
time = ds['time']
bins = ds['bin_depths'].T
north = ds['northward_seawater_velocity'].T
east = ds['eastward_seawater_velocity'].T
up = ds['upward_seawater_velocity'].T

# create dictionary of data, name and units for each variable
time = dict(data=time.data, info=dict(label=time.standard_name, units='GMT'))
bins = dict(data=bins.data, info=dict(label=bins.long_name, units=bins.units))
north = dict(data=north.data, info=dict(label=north.long_name, units=north.units))
east = dict(data=east.data, info=dict(label=east.long_name, units=east.units))
up = dict(data=up.data, info=dict(label=up.long_name, units=up.units))

# create a limit for the colorbar that disregards outliers
colorbar_data = np.concatenate((north['data'], east['data'], up['data']))
lim = float("%2.2f" % np.nanpercentile(abs(colorbar_data), 95))

# set up your plot and give it a title
fig, ax = plt.subplots()
fig.suptitle("ADCP Velocity North")

# plot the north data only
img = plt.pcolormesh(time['data'], bins['data'], north['data'], vmin=-lim, vmax=lim, cmap=plt.get_cmap('jet'))

# format axes and colorbar
max_xticks = 10
ax.xaxis.set_minor_locator(plt.MaxNLocator(max_xticks))
xax = ax.get_xaxis().get_major_formatter()
xax.scaled = {
    365.0 : '%Y-%M', # data longer than a year
    30.   : '%Y-%m\n%d', # set the > 1m < 1Y scale to Y-m
    1.0   : '%m/%d', # set the > 1d < 1m scale to Y-m-d
    1./24.: '%m/%d', # set the < 1d scale to H:M
    1./48.: '%m-%d\n%H:%M:%S',
}

ax.invert_yaxis()
y_formatter = ticker.ScalarFormatter(useOffset=False)
ax.yaxis.set_major_formatter(y_formatter)

div = make_axes_locatable(ax)
cax = div.append_axes("right", size="3%", pad=0.05)
cbar = plt.colorbar(img, cax=cax)
cbar_str = north['info']['label']
cbar.set_label('{}'.format(cbar_str), size=8)
tick_locator = ticker.MaxNLocator(nbins=6)
cbar.locator = tick_locator
cbar.update_ticks()

plt.tight_layout()
plt.savefig('./fig.png', dpi=300)
plt.close('all')







