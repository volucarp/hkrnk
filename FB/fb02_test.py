import unittest
from unittest import TestCase
from fb02_strings import matching_pairs



class TestPermutations(TestCase):
    testcases = [[("abcd", "acdb"), 2]]

    def get_arr(arr_str):
        arr = []
        for s in arr_str.splitlines():
            arr.append(list(map(int, s.rstrip().split())))
            # arr.append(s)
        return arr

    def test_permutation_matched(self):
        for i, case in enumerate(self.testcases):
            res = matching_pairs(*case[0])
            self.assertEqual(case[1], res)


if __name__ == '__main__':
    unittest.main()
