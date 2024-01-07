#%%
class Node:
    def __init__(self, data: int, next=None) -> None:
        self.data = data
        self.next = next

    def get_arr(self):
        ans = []
        node = self
        while node.next:
            ans.append(node.data)
            node = node.next
        ans.append(node.data)
        return ans

def reverse(head:Node):
    orig = head
    ans = None
    while orig.next:
        node = Node(orig.data, ans)
        ans = node
        orig = orig.next
    ans = Node(orig.data, ans)
    return ans

head_node = Node(0, None)
node = head_node
for i in range(1, 9):
    prev_node = node
    node = Node(i, None)
    prev_node.next = node

# %% in-place algo
def reverseIter(head_node):
    mitem = head_node
    previous = None
    while mitem:
        new_next = mitem.next
        #print(mitem.data, end="\n")
        mitem.next = previous
        previous = mitem
        mitem = new_next
    return previous

#%% web
def reverseRecur(head: Node) -> Node:
    if not head: return None
    
    def recurse(curr: Node, nn: Node) -> Node:
        if not nn:
            return None
        nextItem = head.next
        head.next = recurse()

# %%
from FB.checker import Checker
p_checker = Checker()
p_checker.check(
            reverseIter(head_node).get_arr(), 
            [i for i in range(9)][::-1])
# %%
