from itertools import product
from collections import defaultdict
from functools import lru_cache


def sproduct(s1, s2):
        for k, x in enumerate(s1):
            for l, y in enumerate(s2):
                if x == y:
                    yield k, l


# @lru_cache(maxsize=2*1000)
def get_max_subspace(comps: dict, m: int, n: int):
    # max_value, i, j coordinates
    max_so_far = (0, 0, 0)
    for i, j in comps.keys():
        if i<m and j<n:
            if comps[i, j] > max_so_far[0]:
                max_so_far = (comps[i, j], i, j)
        if i==m and j==n:
            break
    max_so_far =  max_so_far[0] + 1,  m,  n
    comps[m, n] = max_so_far[0]
    print(max_so_far)
    return max_so_far



class CharSubsequence:

    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        #. cat.    abcdxyz
        #. crabt.  ocdyyz
        # maybe remove difference of sets
        # cdyz cdyyz
        cset = set(text1).intersection(set(text2))
        n1 = [c for c in text1 if c in cset][::-1]
        n2 = [c for c in text2 if c in cset][::-1]
        r1 = n1[::-1]
        r2 = n2[::-1]
        # state of completions
        comps = defaultdict(int)
        comm_len = 0
        max_val = 0, 0, 0
        glob_max = max_val
        for i, j in sproduct(n1, n2):
            # print(i, j)
            max_val = get_max_subspace(comps, i, j)
            if max_val[0] > glob_max[0]:
                glob_max = max_val  
        comm_len = glob_max[0]
        return comm_len




if __name__ == '__main__':
    import unittest
    from unittest import TestCase

    class TestSolution(TestCase): 

        testcases = [ (("abcde", "ace"), 3),
                    (("abc", "abc"), 3),
                    (("abc", "def"), 0) ]

    def test_solution(self):
        for i, case in enumerate(self.testcases):
            res = CharSubsequence().longestCommonSubsequence(*case[0])
            self.assertEqual(case[1], res, msg=f"at test case {i}") 


    class TestAnothrSub(TestCase):
        def test_more(self):
            res = CharSubsequence().longestCommonSubsequence("abcde", "ace")
            self.assertEqual(3, res)

        unittest.main(verbosity=2)