#%% imports
import pandas as pd 
import numpy as np
from matplotlib import pyplot as plt
from io import StringIO
from IPython.display import display

#%% combine ex
 df1 = pd.DataFrame({'A': [1., np.nan, 3., 5., np.nan],
                     'B': [np.nan, 2., 3., np.nan, 6.]})
 

df2 = pd.DataFrame({'A': [5., 2., 4., np.nan, 3., 7.],
                     'B': [np.nan, np.nan, 3., 4., 6., 8.]})

#paste horizontally
pd.concat([df1, df2], axis=1)

df1.combine_first(df2)
# %%
def combiner(x, y):
    return np.where(pd.isna(x), y, x)

combiner(df1, df2[0:5])
# %% groupby and plot

DataPrefix = "C:/Users/Public/Datasets/pandas/"
air_quality = pd.read_csv(f"{DataPrefix}/air_quality_no2_long.csv")
air_quality = air_quality.rename(columns={"date.utc": "datetime"})
#air_quality['datetime'] = pd.to_datetime(air_quality['datetime'])
air_quality = air_quality.astype({'datetime': 'datetime64[ns, UTC]'}, copy=False)

air_quality.groupby(
   [air_quality["datetime"].dt.weekday, "location"])["value"].mean()
# %% 
fig, axs = plt.subplots(figsize=(12, 4))

air_quality.groupby(
air_quality["datetime"].dt.hour)["value"].mean()\
    .plot(kind='bar', rot=0,ax=axs)
# %% pivot pandas
air_quality.pivot(index="datetime", columns="location", values="value")
# %% read as timestamp

%%timeit
t="""1449054136.83;15.31
1449054137.43;16.19
1449054138.04;19.22
1449054138.65;15.12
1449054139.25;13.12"""
df = pd.read_csv(StringIO(t), header=None, sep=';', index_col=[0])
df.index = pd.to_datetime(df.index, unit='s')

# %%

import time
#  not %%timeit
import time
def date_parser(string_list):
    return [time.ctime(float(x)) for x in string_list]
​
df = pd.read_csv(StringIO(t), parse_dates=[0],  sep=';', 
                 date_parser=date_parser, 
                 index_col='DateTime', 
                 names=['DateTime', 'X'], header=None)
# %%
