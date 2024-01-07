import unittest
from unittest import TestCase
from ch_arrays import hourglassSum, get_arr

class TestHourglassSum(TestCase):

    testcases = {"""1 1 1 0 0 0
0 1 0 0 0 0
1 1 1 0 0 0
0 0 2 4 4 0
0 0 0 2 0 0
0 0 1 2 4 0""": 19,
                 """1 1 1 0 0 0
0 1 0 0 0 0
1 1 1 0 0 0
0 9 2 -4 -4 0
0 0 0 -2 0 0
0 0 -1 -2 -4 0""": 13,
                 """-9 -9 -9 1 1 1
0 -9 0 4 3 2
-9 -9 -9 1 2 3
0 0 8 6 6 0
0 0 0 -2 0 0
0 0 1 2 4 0""": 28}

    def test_hourglassSum(self):
        for i, t in enumerate(self.testcases):
            arr = get_arr(t)
            #print(arr)
            res = hourglassSum(arr)
            self.assertEqual(res, self.testcases[t], msg=f"at test case {i}")


if __name__ == '__main__':
    unittest.main()

