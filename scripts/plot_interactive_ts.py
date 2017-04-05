from bokeh.plotting import figure, output_file, reset_output, show, ColumnDataSource, save
from bokeh.models import BoxAnnotation
from functions import common as cf
import xarray as xr
import re
import numpy as np
import os

tools = 'pan,zoom_in,zoom_out,wheel_zoom,box_zoom,reset,hover'

# t1 = time.time()
def main(nc, save_dir):
    cf.create_dir(save_dir)

    with xr.open_dataset(nc, mask_and_scale=False) as ds:
        subsite = ds.subsite
        node = ds.node
        sensor = ds.sensor
        stream = ds.stream
        deployment = 'D0000{}'.format(str(np.unique(ds.deployment)[0]))
        t0 = ds.time_coverage_start
        t1 = ds.time_coverage_end
        sub_dir = os.path.join(subsite, deployment, node, sensor, stream)

        cf.create_dir(sub_dir)

        misc = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc', 'time', 'mission', 'obs',
                'volt', 'ref', 'sig', 'amp', 'rph', 'calphase', 'phase', 'therm']
        qc = ['qc_results', 'qc_executed']

        reg_ex = re.compile(r'\b(?:%s)\b' % '|'.join(misc))

        #  keep variables that are not in the regular expression
        vars = [s for s in ds.data_vars if not reg_ex.search(s)]
        reg_ex = re.compile('|'.join(qc))
        vars = [s for s in vars if not reg_ex.search(s)]

        x = ds['time'].data

        for v in vars:  # List of dataset variables
            print v
            if ds[v].dtype.kind == 'S' or ds[v].dtype == np.dtype('datetime64[ns]') or 'time' in v:
                continue
            y = ds[v]
            try:
                y_units = y.units
            except AttributeError:
                y_units = None

            y_data = y.data

            if y_data.ndim > 1:
                continue

            source = ColumnDataSource(
                data=dict(
                    x=x,
                    y=y_data,
                )
            )
            gr = cf.get_global_ranges(subsite, node, sensor, v)

            output_file('{}/{}-{}-{}.html'.format(sub_dir, v, ds.time_coverage_start.replace(':', ''), ds.time_coverage_end.replace(':', '')))

            p = figure(width=1200,
                       height=600,
                       title='{}-{}-{}: {} - {} - {}, Stream: {}'.format(subsite, node, sensor, deployment, t0, t1, stream),
                       x_axis_label='Time (GMT)', y_axis_label='{} ({})'.format(v, y_units),
                       x_axis_type='datetime',
                       tools=[tools])
            p.line('x', 'y', legend=v, line_width=3, source=source)
            p.circle('x', 'y', fill_color='white', size=4, source=source)
            if gr:
                low_box = BoxAnnotation(top=gr[0], fill_alpha=0.05, fill_color='red')
                mid_box = BoxAnnotation(top=gr[1], bottom=gr[0], fill_alpha=0.1, fill_color='green')
                high_box = BoxAnnotation(bottom=gr[1], fill_alpha=0.05, fill_color='red')
                p.add_layout(low_box)
                p.add_layout(mid_box)
                p.add_layout(high_box)
            # save(p)
            show(p)
            reset_output()

if __name__ == '__main__':
    nc = 'https://opendap.oceanobservatories.org/thredds/dodsC/ooi/michaesm-marine-rutgers/20170317T160317-CE09OSSM-RID26-07-NUTNRB000-recovered_inst-nutnr_b_instrument_recovered/deployment0001_CE09OSSM-RID26-07-NUTNRB000-recovered_inst-nutnr_b_instrument_recovered_20150409T160033-20150525T210043.nc'
    save_dir = '/Users/mikesmith/Documents/plots'
    main(nc, save_dir)