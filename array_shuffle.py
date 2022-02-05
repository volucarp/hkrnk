import unittest
from unittest import TestCase


def move_zeros_to_left(A):
    # TODONE: Write - Your - Code
    end_pos = len(A) - 1
    read_idx, write_idx = end_pos, end_pos
    while read_idx > -1:
        if A[read_idx] != 0:
            A[write_idx] = A[read_idx]
            write_idx -= 1

        read_idx -= 1

    for j in range(write_idx + 1):
        A[j] = 0
    return A


class TestShufledArray(TestCase):
    array_inputs = [[1, 10, 20, 0, 59, 88, 65, 88, 0]]
    array_should = [[0, 0, 1, 10, 20, 59, 88, 65, 88]]

    def test_array_shuffled(self):
        for i, A in enumerate(self.array_inputs):
            res = move_zeros_to_left(A)
            self.assertEqual(self.array_should[i], res)


if __name__ == '__main__':
    unittest.main()
