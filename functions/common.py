import os
import datetime as dt
import pandas as pd
import requests
import numpy as np


def create_dir(new_dir):
    # Check if dir exists.. if it doesn't... create it.
    if not os.path.isdir(new_dir):
        try:
            os.makedirs(new_dir)
        except OSError:
            if os.path.exists(new_dir):
                pass
            else:
                raise


def compare_lists(list1, list2):
    match = []
    unmatch = []
    for i in list1:
        if i in list2:
            match.append(i)
        else:
            unmatch.append(i)
    return match, unmatch


def reject_outliers(data, m=3):
    # function to reject outliers beyond 3 standard deviations of the mean.
    # data: numpy array containing data
    # m: the number of standard deviations from the mean. Default: 3
    return abs(data - np.nanmean(data)) < m * np.nanstd(data)


def get_rounded_start_and_end_times(timestamp):
    ts0 = to_the_second(pd.to_datetime(timestamp.min()))
    ts1 = to_the_second(pd.to_datetime(timestamp.max()))
    ts_start = round_to_best_hour(ts0)
    ts_end = round_to_best_hour(ts1)
    return ts_start, ts_end


def round_to_best_hour(t):
    delta = dt.timedelta(minutes=t.minute, seconds=t.second,
                         microseconds=t.microsecond)

    down = t - delta # subtract seconds from the time
    up = t + dt.timedelta(seconds=3600) - delta

    if abs(t - up) > abs(t - down):
        return down
    else:
        return up


def to_the_second(ts):
    return pd.Timestamp(long(round(ts.value, -9)))


def get_time_ind(array, t0, t1):
    """
    Returns data (x,y) between start time and end time
    :param array: Numpy array of datenums
    :param t0: Start datetime
    :param t1: End datetime
    :return: Index between start and end datetimes
    """
    time_ind = np.where((array >= t0) & (array <= t1))
    return time_ind


def get_global_ranges(platform, node, sensor, variable):
    url = 'http://ooiufs01.ooi.rutgers.edu:12578/qcparameters/inv/{}/{}/{}/'.format(platform, node, sensor)

    r = requests.get(url)

    # if r.status_code is 200:
    values = pd.io.json.json_normalize(r.json())
    t1 = values[values['qcParameterPK.streamParameter'] == variable]
    t2 = t1[t1['qcParameterPK.qcId'] == 'dataqc_globalrangetest_minmax']
    local_min = t2[t2['qcParameterPK.parameter'] == 'dat_min'].iloc[0]['value']
    local_max = t2[t2['qcParameterPK.parameter'] == 'dat_max'].iloc[0]['value']
    return [int(local_min), int(local_max)]
