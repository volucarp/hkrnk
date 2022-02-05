import unittest
from unittest import TestCase
from math import inf

#%%
class Pair:
  def __init__(self, first, second):
    self.first = first
    self.second = second

  def __repr__(self):
      return(f"({self.first}, {self.second})")

def merge_intervals(v):
  if v == None or len(v) == 0 :
    return None

  result = []
  result.append(Pair(v[0].first, v[0].second))

  for i in range(1, len(v)):
    x1 = v[i].first
    y1 = v[i].second
    x2 = result[len(result) - 1].first
    y2 = result[len(result) - 1].second

    if y2 >= x1:
      result[len(result) - 1].second = max(y1, y2)
    else:
      result.append(Pair(x1, y1))

  return result

v = [Pair(1, 5), Pair(3, 1), Pair(4, 6),
     Pair(6, 8), Pair(10, 12), Pair(11, 15)]

result = merge_intervals(v)

for i in range(len(result)):
  print("[" + str(result[i].first) + ", " + str(result[i].second) + "]", end =" ")


# %% Unfinished
""" The previous one amends last element of result array and scans from 1 to len() which are the good tricks """
def merge_pairs_2(A):
    """Given input array of tuples return merged tupples"""
    low, high = inf, -inf
    res = []
    prev_start = None
    prev_finish = None
    for (start, finish) in A:
        if prev_start is None:
            prev
        low = min(low, start)
        if start < high:
            high = max(finish, high)
        else:
            low = start
            high = finish
        res.append((low, high))
        prev_start = start
        prev_finish = finish
    return res

print(merge_pairs([(1, 2)]))
print(merge_pairs([(1, 2), (3,4 )]))
print(merge_pairs([(1, 3), (2,4 )]))


#%%
# merge(fuse) two sorted linked lists
def concatenate_lists(head1, head2):
    if head1 == None:
        return head2

    if head2 == None:
        return head1

    # use left for previous.
    # use right for next.
    tail1 = head1.left
    tail2 = head2.left

    tail1.right = head2
    head2.left = tail1

    head1.left = tail2
    tail2.right = head1
    return head1


def convert_to_linked_list(root):
    if root == None:
        return None

    list1 = convert_to_linked_list(root.left)
    list2 = convert_to_linked_list(root.right)

    root.left = root.right = root
    result = concatenate_lists(list1, root)
    result = concatenate_lists(result, list2)

    return result


def get_list(head):
    r = []
    if head == None:
        return r

    temp = head
    while True:
        r.append(temp.data)
        temp = temp.right
        if temp == head:
            break

    return r


def test(orig_data):
    root = create_BST(orig_data)

    all_data = bst_to_list(root)
    # print(all_data);

    head = convert_to_linked_list(root)
    # print_list(all_data)
    # print_list(v)

    return head


def main():
    data = [100, 50, 200, 25, 75, 350]
    res = test(data)
    v = get_list(res)
    print_list(v)



main()
#%%
class TestMergedPairs(TestCase):
    array_inputs = [[(1,5), (3,7), (4,6), (6,8), (10, 11)]]
    array_should = [[(1,8), (10,11)]]

    def test_merged(self):
        for i, A in enumerate(self.array_inputs):
            res = merge_pairs(A)
            self.assertEqual(self.array_should[i], res)


if __name__ == '__main__':
    unittest.main()