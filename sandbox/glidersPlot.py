import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import os

# file = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/ooi/michaesm-marine-rutgers/9e94eeb6-5001-4006-8687-f4c4c897b4a4/deployment0002_CP05MOAS-GL387-03-CTDGVM000-recovered_host-ctdgv_m_glider_instrument_recovered.ncml'
# file = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/ooi/michaesm-marine-rutgers/9e75f89e-7db2-4a6b-9097-e91068f6bc71/deployment0002_CP05MOAS-GL387-01-ADCPAM001-recovered_host-adcpa_m_glider_recovered.ncml'
# file = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/ooi/michaesm-marine-rutgers/e4b67a61-aeb5-4bec-bd23-5c63e807d41f/deployment0002_CP05MOAS-GL387-04-DOSTAM000-recovered_host-dosta_abcdjm_glider_recovered.ncml'
# file = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/ooi/michaesm-marine-rutgers/39c55431-3f6d-49c5-a3be-a7518dc564c3/deployment0002_CP05MOAS-GL387-05-PARADM000-recovered_host-parad_m_glider_recovered.ncml'
# file = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/ooi/michaesm-marine-rutgers/96b320c3-8571-4b5f-8b09-632bd06f5c0f/deployment0003_CP05MOAS-GL387-02-FLORTM000-telemetered-flort_m_glider_instrument.ncml'
# file = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/ooi/michaesm-marine-rutgers/5c2184a5-f0a1-4e0e-aba1-d25aaf724740/deployment0003_CP05MOAS-GL387-04-DOSTAM000-telemetered-dosta_abcdjm_glider_instrument.ncml'
# file = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/timeseries/Coastal_Pioneer/CP05MOAS/02-FLORTM000/telemetered/CP05MOAS-GL376-02-FLORTM000-flort_m_glider_instrument-telemetered/CP05MOAS-GL376-02-FLORTM000-flort_m_glider_instrument-telemetered.ncml'

f = nc.Dataset(file)
# print f.time_coverage_start + ' ' + f.time_coverage_end

for vars in f.variables:
    try:
        units = f.variables[vars].units
    except AttributeError:
        pass
        units = 'n/a'

    try:
        dif = np.diff(f.variables[vars][:])
        dM = np.nansum(np.abs(dif))
    except:
        pass
        dM = 'n/a'

    print os.path.basename(file) + ',' + f.time_coverage_start + ',' + f.time_coverage_end + ',' + vars + ',' + units + ',' + str(dM)

# nc_vars = [str(var) for var in f.variables]
lon = f.variables['lon']
lat = f.variables['lat']
depth = f.variables['pressure_depth']
timeR = f.variables['time']

time = nc.num2date(timeR[:], timeR.units)

plt.subplot(3,1,1)
plt.plot(time, lon)
plt.ylabel('Lon')
plt.title(os.path.basename(file))
plt.plot(time, lat)
plt.ylabel('Lat')
plt.plot(time, depth)
plt.ylabel('Depth')

# # Fine-tune figure; make subplots close to each other and hide x ticks for
# # all but bottom plot.
# f.subplots_adjust(hspace=0)
# # plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
#
plt.plot()
# plt.show()
plt.savefig(os.path.basename(file)+'-plot.png',dpi=100) # save figure
plt.close()