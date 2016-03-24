#! /usr/bin/env python
from thredds_crawler.crawl import Crawl
C = Crawl("http://opendap-devel.ooi.rutgers.edu:8090/thredds/catalog/first-in-class/Coastal_Endurance/catalog.xml", select=[".*ncml"])

tds = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/'
fopen = open('/Users/michaesm/Documents/thredds-links.txt', 'w')

for dataset in C.datasets:
    fopen.write(tds + dataset.id + '\n')

fopen.close()