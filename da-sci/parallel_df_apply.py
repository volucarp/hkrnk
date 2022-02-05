# %% imports

import numpy as np
import pandas as pd
from functools import partial
import time
import timeit
import concurrent 


# %% start definitions
# a no op function that simulates a transformation that takes some time to complete
def do_work(row, duration):
    time.sleep(duration)
    return True

FUNCTION_RUN_TIME = 0.0001

# %% setup
def setup():
    return pd.DataFrame(np.random.binomial(n=1000, p=0.2, size=(10000,2)))

# %% parallilize simple function
def sum_square(a, b):
    return (a+b)**2

def df_col_square(df):
    return (df[0]+df[1])**2

#parallelized sum of squares:
psum_square = partial(sum_square)


# %% example for serial function
# simple use of apply to execute the function against the pd dataframe
def serial_calc(df, duration):
    apply_partial = partial(do_work, duration=duration)
    df['result'] = df.apply(apply_partial, axis=1)
    return df

#%timeit serial_calc(df, FUNCTION_RUN_TIME)

# %% running serial func in parallel
# simple wrapper code around serial_calc to parallelize the work
def parallel_calc(df, func, n_core, duration):
    futs = []
    df_split = np.array_split(df, n_core)
#     pool = concurrent.futures.ThreadPoolExecutor(max_workers = n_core)
    pool = concurrent.futures.ProcessPoolExecutor(max_workers = n_core)
    apply_partial = partial(func, duration=duration)
    return pd.concat(pool.map(apply_partial, df_split))

#%timeit parallel_calc(df, serial_calc, 32, FUNCTION_RUN_TIME)

def main():
    df = setup()
    #time execution of psum_square
    #timeit.timeit(psum_square(df[0], df[1]), number=3)

    #timeit.timeit(parallel_calc(df, serial_calc, 32, FUNCTION_RUN_TIME), number=1)
    #print imting stats
    print (timeit.timeit(setup = "df = setup()", 
                     stmt = "parallel_calc(df, serial_calc, 32, FUNCTION_RUN_TIME)",
                     number = 10))

# %% main execution
if __name__ == '__main__':
    main()
# %%
