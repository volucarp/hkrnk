#%% Pop/append Insert
my_list = [1, 2, 3]

my_list.append(4) # [1, 2, 3, 4] O(1)
my_list.append(5) # [1, 2, 3, 4, 5]   O(1)

my_list.pop() # [1, 2, 3, 4]  # O(1)

my_list.insert(1, 3) # [1, 3, 2, 3, 4] O(N)

#%% dictionaries

my_dict = {"a": 1, "b": 2, "c": 3}
values = my_dict.values()
print(values)  # dict_values([1, 2, 3])
values_list = list(values)
print(values_list)  # [1, 2, 3]

#%% sets
my_set = {'a'}

my_set.remove('a') # {}
my_set.remove('a') # KeyError

my_set.add('b') # {'b'}
my_set.discard('b') # {}
my_set.discard('b') # {} (no error)

#%% heaps

import heapq
from typing import List


def heap_push(heap: List[int], value: int) -> int:
    pass


# do not modify below this line
print(heap_push([1, 2, 3], 4))
print(heap_push([1, 2, 3], 0))
print(heap_push([1, 2, 3], 2))
print(heap_push([4, 6, 7, 8, 12, 9, 10], 2))
print(heap_push([4, 6, 7, 8, 12, 9, 10], 5))