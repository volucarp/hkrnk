#!/bin/env python

#%%
import math
import os
import random
import re
import sys
import numpy as np


#%% testing mask
# Complete the hourglassSum function below.
def hourglassSum(arr):
    #import numpy as np
    from pprint import pprint
    mask = [[0,1,2],[1],[0,1,2]]
    #npmask = np.array(mask)
    #nparr = np.array(arr)
    t, w = 6, 6
    npres = []
    for it in range(t-2):
        for iw in range(w-2):
            #print( it, iw)
            hsum = 0
            for itm, _ in enumerate(mask):
                for iwm in mask[itm]:
                    hsum += arr[it+itm][iw+iwm]
            npres.append(hsum)
    #pprint(npres)
    maxsum = max(npres)
    return maxsum


def get_arr(arr_str):
    arr = []
    for s in arr_str.splitlines():
        arr.append(list(map(int, s.rstrip().split())))
        #arr.append(s)
    return arr


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    arr = []

    for _ in range(6):
        arr.append(list(map(int, input().rstrip().split())))

    result = hourglassSum(arr)

    fptr.write(str(result) + '\n')
    fptr.close()
