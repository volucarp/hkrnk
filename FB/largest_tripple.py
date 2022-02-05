# %%
import math
from FB.checker import Checker
import heapq

problem = Checker()
h = heapq.heapify([])

# %% straightforward
import math
import operator
import random


class TopN(object):

    def __init__(self, n=2, init=-math.inf, f=operator.ge):
        self.cache = [-math.inf] * n
        self.init = init
        self.f = f
        self.lim = init
        self.N = n
        self.op = 0

    def get_nops(self):
        return self.op

    def add(self, element, start=0):
        if self.f(self.lim, element):
            self.op += 1
            return False

        for idx in range(start, len(self.cache)):
            val = self.cache[idx]
            self.op += 1
            if self.f(element, val):
                self.op += 1
                self.cache[idx] = element
                if self.N == idx:
                    self.lim = element
                else:
                    self.add(val, start=idx + 1)

                return True
        return False

    def __repr__(self):
        return '[' + ', '.join([str(i) for i in self.cache]) + ']'


top3 = TopN(n=300)

# for i in range(20):
#     top3.add(i)
#
# top3.add(19)
# for i in range(18):
#     top3.add(i)


for N in range(int(1e6)):
    el = random.randint(1, 10000000)
    top3.add(el)

print(top3)
print(top3.get_nops())


# %% heap performance
class BinHeap:
    def __init__(self):
        self.heapList = [0]
        self.currentSize = 0

    def percUp(self, i):
        while i // 2 > 0:
            if self.heapList[i] < self.heapList[i // 2]:
                tmp = self.heapList[i // 2]
                self.heapList[i // 2] = self.heapList[i]
                self.heapList[i] = tmp
            i = i // 2

    def insert(self, k):
        self.heapList.append(k)
        self.currentSize = self.currentSize + 1
        self.percUp(self.currentSize)


#%%
class AnyLimHeap:
    def __init__(self, size=3, init=-math.inf, op=operator.ge):
        self.heap_list = [0.] + [init] * size
        self.size = size
        self.nops = 0
        self.op = op

    def __repr__(self):
        return '[' + ', '.join([str(i) for i in self.heap_list]) + ']'

    def swap_at(self, i):
        self.nops += 1
        tmp = self.heap_list[i // 2]
        self.heap_list[i // 2] = self.heap_list[i]
        self.heap_list[i] = tmp

    def push_root(self, i):
        while i // 2 > 0:
            self.nops += 1
            if self.op(self.heap_list[i], self.heap_list[i // 2]):
                self.swap_at(i)
            i = i // 2

    def swap_idx(self, i, j):
        self.nops += 1
        tmp = self.heap_list[i]
        self.heap_list[i] = self.heap_list[j]
        self.heap_list[j] = tmp

    def bubble_up(self, at=1):
        if 2* at + 1 < self.size:
            if self.op(self.heap_list[2*at], self.heap_list[2*at + 1]):
                new_at = 2*at + 1
            else:
                new_at = 2*at
            if self.op(self.heap_list[at], self.heap_list[new_at]):
                self.swap_idx(at, new_at)
                self.bubble_up(new_at)

    def add(self, element):
        if self.op(element, self.heap_list[1]):
            self.heap_list[1] = element
            self.bubble_up()


top_heap = AnyLimHeap(size=8)
for i in range(1, 1):
    top_heap.add(i)

print(top_heap)
print(top_heap.nops)


# %%
def findMaxProduct(arr):
    # Write your code here

    import heapq
    h = []
    res = []
    for idx, value in enumerate(arr):
        heapq.heappush(h, value)
