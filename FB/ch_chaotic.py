import math
import os
import random
import re
import sys


# Complete the minimumBribes function below.
def dist(i, n):
    "Returns number of switches for the current label"
    from math import inf
    a = max(0, i-n+1)
    b = max(0, n-i-1)
    return a if b <= 2 else inf


# Complete the minimumBribes function below.
def minimum_bribes_case(q):
    res = [ dist(i, n) for i, n in enumerate(q)]
    #print(res)
    total = sum(res)
    return total


def minimum_bribes(qarr):
    res = minimum_bribes_case(qarr)
    print(f"{res}" if res != math.inf else "Too chaotic")



if __name__ == '__main__':
    t = int(input())

    for t_itr in range(t):
        n = int(input())

        q = list(map(int, input().rstrip().split()))

        minimum_bribes(q)