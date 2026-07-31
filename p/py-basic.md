## List Time Complexity

```python
my_list = [1, 3, 2, 3]

my_list.index(3) # 1

my_list.remove(3) # [1, 2, 3]

my_list.extend([4, 5]) # [1, 2, 3, 4, 5]

items.index(x)
items.remove(x)
items.extend(other)
x in items
```

| Operation | Time complexity |
| --- | --- |
| `items.index(x)` | `O(n)` |
| `items.remove(x)` | `O(n)` |
| `items.extend(other)` | `O(m)` |
| `x in items` | `O(n)` |

- `n`: length of the list
- `m`: length of the iterable passed to `extend()`

## List concat/ extend

```py

list1 = [1, 2, 3]
list2 = [4, 5, 6]

result = list1 + list2 # [1, 2, 3, 4, 5, 6] => O(n+m)
list1.extend(list2)    # O(m)
```

```py
import copy
original_list = [[1, 2], [3, 4]]
cloned_list = copy.deepcopy(original_list)

original_list = [[1, 2], [3, 4]]
cloned_list = original_list.copy()

cloned_list[0][0] = 99
print(original_list)  # [[99, 2], [3, 4]]
```

## Stack

```py
stack = []

stack.append(1)   # push
stack.append(2)   # push
stack.pop()       # 2
stack[-1]         # peek -> 1
len(stack) == 0   # is empty
```

| Operation | Time complexity |
| --- | --- |
| `stack.append(x)` | `O(1)` |
| `stack.pop()` | `O(1)` |
| `stack[-1]` | `O(1)` |
| `len(stack) == 0` | `O(1)` |

## Queue

```py
from collections import deque

queue = deque()

queue.append(1)    # enqueue
queue.append(2)    # enqueue
queue.popleft()    # 1
queue[0]           # peek -> 2
len(queue) == 0    # is empty
```

| Operation | Time complexity |
| --- | --- |
| `queue.append(x)` | `O(1)` |
| `queue.popleft()` | `O(1)` |
| `queue[0]` | `O(1)` |
| `len(queue) == 0` | `O(1)` |

## Heap Push

Heaps / priority queues pop by priority. Python `heapq` is a min heap, so the smallest value is at index `0`.

```py
import heapq

heap = []  # min heap

heapq.heappush(heap, 3)  # O(log n)
heapq.heappush(heap, 1)  # O(log n)

print(heap[0])  # 1, peek O(1)

heapq.heappush(heap, 0)  # O(log n)

print(heap[0])  # 0, peek O(1)
```

## Depth-First Search

DFS visits nodes by going as deep as possible before backtracking. For binary trees, the three common recursive traversals are inorder, preorder, and postorder.

```py
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def inorder(root):
    if not root:
        return

    inorder(root.left)
    print(root.val)
    inorder(root.right)


def preorder(root):
    if not root:
        return

    print(root.val)
    preorder(root.left)
    preorder(root.right)


def postorder(root):
    if not root:
        return

    postorder(root.left)
    postorder(root.right)
    print(root.val)
```

| Traversal | Order |
| --- | --- |
| Inorder | left, root, right |
| Preorder | root, left, right |
| Postorder | left, right, root |

| Complexity | Value |
| --- | --- |
| Time | `O(n)` |
| Space | `O(h)` |

- `n`: number of nodes
- `h`: tree height
- Balanced tree space: `O(log n)`
- Skewed tree space: `O(n)`
- Inorder traversal of a BST visits values in sorted order.

## Breadth-First Search

BFS visits all nodes on one level before moving to the next. For trees, this is also called level-order traversal.

```py
from collections import deque


class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def bfs(root):
    queue = deque()

    if root:
        queue.append(root)

    level = 0
    while queue:
        print("level:", level)

        for _ in range(len(queue)):
            curr = queue.popleft()
            print(curr.val)

            if curr.left:
                queue.append(curr.left)
            if curr.right:
                queue.append(curr.right)

        level += 1
```

| Operation | Purpose |
| --- | --- |
| `queue.append(node)` | add next-level node |
| `queue.popleft()` | visit current-level node |
| `range(len(queue))` | process one level at a time |

| Complexity | Value |
| --- | --- |
| Time | `O(n)` |
| Space | `O(n)` |

- `n`: number of nodes
- Queue stores one level at a time.
- Worst case space is `O(n)` because the largest level can contain many nodes.
