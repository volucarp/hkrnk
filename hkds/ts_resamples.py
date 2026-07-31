#%%
import pandas as pd
import numpy as np
from datetime import date, timedelta

#%%
# Choose your 1-month window (example: last 30 days)
d2 = date.today()
d1 = d2 - timedelta(days=45)

url = (
    "https://stooq.com/q/d/l/"
    f"?s=aapl.us&i=d&d1={d1:%Y%m%d}&d2={d2:%Y%m%d}"
)

df = pd.read_csv(url)
df["Date"] = pd.to_datetime(df["Date"])
df = df.set_index("Date").sort_index()

#%%
df.head()
# %%
"""
wrong: tries to use columns:
  !!! df.groupby(df.index.to_period("M")).agg("mean_monthly", lambda x: np.mean(x.Open + x.Close) / 2)
  
aggregations:
1)    .agg(new_col_name=("existing_col_name", aggfunc))
2)   mean_monthly = (
        df.groupby(df.index.to_period("M")
        ).apply(
            lambda g: ((g["Open"] + g["Close"]) / 2
        ).mean()
    ).to_frame("mean_monthly")
3) build / aggregate
mean_monthly = ((df["Open"] + df["Close"]) / 2).groupby(df.index.to_period("M")).mean()
4) id datetime is index, can resample:
"""


# %%

# %%
mean_monthly = (
    (df["Open"] + df["Close"]) / 2
    ).resample("ME"
    ).mean(
    ).rename(
        "mean_monthly"
    ).to_frame()
# %%
