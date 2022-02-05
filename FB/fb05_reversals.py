#%%
import math
from collections import defaultdict


from FB.checker import Checker

problem = Checker()


#%%
def def_value():
    return []


d = defaultdict(def_value())

#%% solution
invocation_cnt = 0
def reverse(Arr, st, fin, num_invocations = 0):
    if st >= fin:
        return Arr, num_invocations

    num_invocations += 1

    j = 0
    for i in range(st, st + int((fin+1-st)/2)):
        #print (i, Arr[i], Arr[fin-i])
        tmp = Arr[i]
        Arr[i] = Arr[fin-j]
        Arr[fin-j] = tmp
        j+=1
    return Arr, num_invocations

Arr = [1, 2, 3, 4, 8, 7, 5, 6]
reverse(Arr, 4, 6)
#%%
invocation_cnt = 0
def minOperations(Arr):
    num_invocations = 0
    sorted_arr = sorted(Arr)
    for idx_sorted, el_sorted in enumerate(sorted_arr):
        idx_arr = idx_sorted
        while  idx_arr < len(Arr) and Arr[idx_arr] != el_sorted:
            idx_arr += 1
        #print(Arr, idx_sorted, idx_arr)
        Arr, num_invocations = reverse(Arr, idx_sorted, idx_arr, num_invocations)

    return num_invocations, Arr
        #for idx_arr, el_arr in enumerate(Arr):


minOperations([4, 3, 2, 1, 8, 7, 5, 6])

#%% Leet Solution
import heapq

def is_sorted(arr):
    for i in range(1, len(arr)):
        if arr[i] < arr[i - 1]:
            return False
    return True


def utility(arr):
    cnt = 0
    for i in range(1, len(arr)):
        if arr[i] == arr[i - 1] + 1 or arr[i] == arr[i - 1] - 1:
            cnt += 1
    return cnt


def min_inversions(arr):
    u = utility(arr)
    heap = [(-u, 0, arr[:])]
    min_cost, out = float("Inf"), []
    cache = {}

    while len(heap) > 0:
        v, cost, a = heapq.heappop(heap)

        if is_sorted(a):
            min_cost = min(min_cost, cost)
            out = a

        elif cost < min_cost:
            for i in range(len(a) - 1):
                for j in range(i + 1, len(a)):
                    b = a[:]
                    b[i:j + 1] = b[i:j + 1][::-1]

                    if tuple(b) not in cache or cache[tuple(b)] > cost + 1:
                        u = utility(b)
                        heapq.heappush(heap, (-u, cost + 1, b))
                        cache[tuple(b)] = cost + 1
    return min_cost

minOperations = min_inversions

#%%checking
if __name__ == "__main__":
    n_1 = 5
    arr_1 = [1, 2, 5, 4, 3]
    expected_1 = 1
    output_1 = minOperations(arr_1)
    problem.check(expected_1, output_1)

    n_2 = 3
    arr_2 = [3, 1, 2]
    expected_2 = 2
    output_2 = minOperations(arr_2)
    problem.check(expected_2, output_2)

    # Add your own test cases here
    problem.check(3, minOperations([4, 3, 2, 1, 8, 7, 5, 6]))

    problem.check(2, minOperations([ 8, 7, 5, 6, 4, 3, 2, 1]))

    problem.check(2, minOperations([ 8, 9, 1, 7, 6, 5, 4]))

    problem.check(4, minOperations([11, 13, 9, 4, 5, 7]))
