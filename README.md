# plot-nc-ooi
This toolbox contains python scripts that plot netCDF datasets.

##Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Functions](#functions)
- [Scripts](#scripts)
- [Data Format](#data format)

###Introduction
This toolbox was created for the Ocean Observatories Initiative (OOI) data review team to easily plot netCDF files located on THREDDS Data Servers (TDS) via OPeNDAP. This toolbox is built on top of matplotlib to provide an easier way to make 'pretty' plots of scientific data. These functions automatically scale axes and add titles/labels to plots provided the data is in a dictionary format that the toolbox functions are designed to read.

- Author: Mike Smith - Rutgers University - michaesm@marine.rutgers.edu


###Installation
    > git clone https://github.com/ooi-data-review/plot-nc-ooi.git
    > cd plot-nc-ooi
    > pip install .
    > pip install -r requirements.txt

###Functions
In this toolbox, there is a directory, functions, which contains two sets of helper functions.
- [common.py]: This set of functions that can be imported both by a user creating a new plotting routine and by functions.plotting.
- [plotting.py]: This set of functions easily creates different plot types depending on the structure of the data that needs to be plotted.

See the wiki for more information regarding all functions contained within this toolbox.

###Scripts
There are currently four scripts included with this toolbox.
- [plot_timeseries.py](https://github.com/ooi-data-review/plot-nc-ooi/blob/master/plot_timeseries.py): This plots all variables contained in a designated netCDF4 file. It automatically switches between plot, nan_plot (plot when data is all nans), and multiline (multidimensional arrays) based on the shape of the data. 

- [plot_compare_timeseries_monthly.py](https://raw.githubusercontent.com/ooi-data-review/plot-nc-ooi/master/scripts/plot_compare_timeseries_monthly.py): This script is used to generate timeseries plots that display distinct timeseries datasets by month on the same plot.

- [plot_timeseries_compare_outliers.py](https://raw.githubusercontent.com/ooi-data-review/plot-nc-ooi/master/scripts/plot_timeseries_compare_outliers.py): This script is used to generate timeseries plots that display a timeseries dataset with outliers present and removed on the same plot. An outlier is defined as a default of +/- 1 standard deviation, but can be defined by the user.

- [plot_adcp.py] (https://raw.githubusercontent.com/ooi-data-review/plot-nc-ooi/master/scripts/plot_adcp.py): This script is used to generate pcolormesh plots of adcp data. The colormap is dynamically scaled based on the 95th percentile of the data present. 

###Data Format
When passing data into plotting functions, the data must be in the following dictionary format for both x and y variables:
var = {'data': numpy data array , 'info': {'label': axis label, 'units': axis units', 'var': variable name, 'platform': platform name, 'node': node name, 'sensor': sensor name}}

An easy way to create the dictionary in a single line of code is as follows:
- y = dict(data=sci.data, info=dict(label=y_lab, units=sci.units, var=var, platform=platform, node=node, sensor=sensor))
