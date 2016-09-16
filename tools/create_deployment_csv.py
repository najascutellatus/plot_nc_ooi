import glob
import pandas as pd
import os
import datetime
import calendar

deployments = glob.glob('/Users/michaesm/Documents/dev/repos/petercable/asset-management-proto/deployment/*.csv')
save_dir = ''

if not save_dir:
    save_dir = os.getcwd()

data = []

df = pd.DataFrame()

for deployment in deployments:
    df_t = pd.read_csv(deployment)
    df = df.append(df_t)
    # startTime = pd.unique(df.startDateTime.ravel())[0]
    # endTime = pd.unique(df.stopDateTime.ravel())[0]
    # deploymentNumber = pd.unique(df.deploymentNumber.ravel())[0]
    # platform = os.path.basename(deployment)[:8]
    # data.append((platform, deploymentNumber, startTime, endTime))

# df = pd.DataFrame(data, columns=['platform', 'deployment', 'start_date', 'end_date'])
dt = datetime.datetime.now()
df.to_csv('{}/deployments_{}{}.csv'.format(save_dir, dt.year, calendar.month_name[dt.month]), index=False)