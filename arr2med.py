#%%
nums1 = [1, 3, 7, 9, 14, 20 , 35]
nums2 = [1, 3, 7, 9, 14, 20 ]
nums3 = []

len(nums1)
# %%

def get_median(arr) -> float :
    l = len(arr)
    if l == 0 :
        return None
    if l % 2 == 0 :
        return (arr[l//2] + arr[l//2+1]) /2.
    return arr[l//2]

print(get_median(nums1))
print(get_median(nums2))
print(get_median(nums3))
# %%
class Solution:
    def findMedianSortedArrays(self, 
            nums1: list[int], 
            nums2: list[int]
            ) -> float:
        n = len(nums1)
        m = len(nums2)
# %%
