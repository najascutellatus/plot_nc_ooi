import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import urllib2
from xml.dom import minidom
import re
import os


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

def getMultipleVariables(library):
    multiVarLib = [] # Create empty list for y variables and metadata
    for variable in library:
        var = str(raw_input("Variable: %s"%variable + " <n> : ")) or 'n'
        if var == 'y':
            multiVarLib.append(variable)
    return multiVarLib

def reject_outliers(data, m=2):
    return abs(data - np.mean(data)) < m * np.std(data)


url = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/catalog/eov-1/catalog.xml'
opendap = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/'
arrayOOI = iterate_items(url)
ncmlList = []

# sI = raw_input("Enter list of sensors (comma-separated, all caps): ")
# sI = sI.split(',')
reX = 'CTDGV'

# selectedArrays = getMultipleVariables(arrayOOI)
# print "Arrays Selected"
print ' '
print ' '

for urls in arrayOOI:
    platformOOI = iterate_items(urls)
    # print platformOOI
    for platforms in platformOOI:
        if 'MOAS' in platforms:
            # print platforms
            instrumentOOI = iterate_items(platforms)
            instrumentOOISel = [s for s in instrumentOOI if reX in s]
            # print instrumentOOI
            for instruments in instrumentOOISel:
                deliveryMTD = iterate_items(instruments)

                for methods in deliveryMTD:
                    streams = iterate_items(methods)
                    for stream in streams:
                        if 'eng' in stream:
                            continue
                        elif 'metadata' in stream:
                            continue
                        else:
                            'Continuing'
                        (root, ext) = os.path.splitext(stream)
                        streamURL = root + '.html'
                        dataset = iterate_data(stream)
                        ncml = [s for s in dataset if '.nc' in s]
                        ncmlList.append(opendap + ncml[0])

for file in ncmlList:
    f = nc.Dataset(file)
    lon = f.variables['lon']
    lat = f.variables['lat']
    depth = f.variables['int_ctd_pressure']
    timeR = f.variables['time']

    lonInd = reject_outliers(lon)
    lon = lon[lonInd]
    lat = lat[lonInd]
    timeR = timeR[lonInd]

    latInd = reject_outliers(lat)
    lat = lat[latInd]
    lon = lon[latInd]
    timeR = timeR[latInd]

    time = nc.num2date(timeR[:], timeR.units)

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)

    ax1.plot(timeR, lon)
    ax1.set_title('Lon/Lat/Depth')
    ax2.plot(timeR, lat)
    ax3.plot(timeR, depth)
    # Fine-tune figure; make subplots close to each other and hide x ticks for all but bottom plot.
    fig.subplots_adjust(hspace=0)
    # plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    plt.plot()
    plt.close()
