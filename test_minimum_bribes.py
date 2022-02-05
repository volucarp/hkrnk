from unittest import TestCase
import unittest
from ch_chaotic import minimum_bribes_case
import math


def get_arr(s):
    return [ int(i) for i in s.strip().split()]


class TestMinimum_bribes(TestCase):

    testcases = {"1 2 5 3 7 8 6 4": 7,
                 "2 5 1 3 4": math.inf}

    def test_minimum_bribes(self):
        for i, t in enumerate(self.testcases):
            arr = get_arr(t)
            res = minimum_bribes_case(arr)
            print(t, self.testcases[t])
            self.assertEqual(res, self.testcases[t], msg=f"at test case {i}")


if __name__ == '__main__':
    unittest.main()