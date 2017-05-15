#! /usr/bin/env python
from thredds_crawler.crawl import Crawl
import click as click
import datetime as dt
import os
import functions.common as cf


@click.command()
@click.argument('url', nargs=1, type=click.Path())
@click.argument('out', nargs=1, type=click.Path(exists=False))
def main(url, out):
    now = dt.datetime.now().strftime('%Y.%m.%dT%H.%M.00')
    C = Crawl(url, select=[".*ncml"])
    tds = 'https://opendap.oceanobservatories.org/thredds/dodsC/'
    cf.create_dir(out)
    fopen = open(out+ '/' + now+'-nc-links.txt', 'w')

    for dataset in C.datasets:
        fopen.write(tds + dataset.id + '\n')

    fopen.close()

if __name__ == '__main__':
    main()
