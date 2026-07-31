#%% timezone-aware pandas datetime example
import pandas as pd
def create_timezone_aware_ts(df: pd.DataFrame) -> pd.Series:
    ts = (
        pd.to_datetime(df["ts_raw"])
        .dt.tz_localize(
            "America/New_York",
            ambiguous="NaT",
            nonexistent="shift_forward"
        )
        .dt.tz_convert("UTC")
    )
    return ts

#%% ts-cheat-sheet
# string or numeric → datetime UTC
from typing import List, Optional, Union

def cs_dt(df: Union[pd.Series,pd.DataFrame], cols: List[str], x):
    "cheat sheet for pandas datetime conversions"
    df["ts"] = pd.to_datetime(df["raw"], utc=True)

    # multiple columns
    df[cols] = df[cols].apply(pd.to_datetime, utc=True)

    # unix timestamps
    pd.to_datetime(x, unit="s", utc=True)

    # date only
    df["date"] = df["ts"].dt.date

#%% tz-naive values
def cmp_tz(ts):
    ts = ts.tz_convert("America/New_York")
    is_open = (
        (ts.dt.time >= pd.to_datetime("09:30").time()) &
        (ts.dt.time <= pd.to_datetime("16:00").time())
    )
    return is_open

#%% test cases and demos
import pandas as pd

df = pd.DataFrame({
    "ts_raw": [
        "2024-06-03 09:29:00",  # before open
        "2024-06-03 09:30:00",  # open
        "2024-06-03 12:00:00",  # intraday
        "2024-06-03 16:00:00",  # close
        "2024-06-03 16:01:00",  # after close
    ],
    "symbol": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
    "price": [187.1, 187.5, 189.2, 188.9, 188.7],
})


# %% running
ts = create_timezone_aware_ts(df)
ts_ny = ts.dt.tz_convert("America/New_York")
# .dt.time returns tz-naive time only

df["is_open"] = (
    (ts_ny.dt.time >= pd.to_datetime("09:30").time()) &
    (ts_ny.dt.time <= pd.to_datetime("16:00").time())
)


# %%
def conversions(ts):
    (ts 
    .dt.tz_convert("America/New_York")
    .dt.tz_localize(None).astype("datetime64[s]")
    .dt.floor("D").to_numpy().view("int64"))


#%% groupings
out = df.groupby("py").agg(
    sum_usd=("usd", "sum"),
    items=("ticker", "nunique"),
)