from typing import List, Deque
from collections import deque


def rotate_list(arr: List[int], k: int) -> Deque[int]:
    rotated = deque(arr)
    if rotated:
        rotated.rotate(k % len(rotated))
    return rotated


def _run_tests() -> None:
    assert list(rotate_list([1, 2, 3, 4, 5], 0)) == [1, 2, 3, 4, 5]
    assert list(rotate_list([1, 2, 3, 4, 5], 1)) == [5, 1, 2, 3, 4]
    assert list(rotate_list([1, 2, 3, 4, 5], 2)) == [4, 5, 1, 2, 3]
    assert list(rotate_list([1, 2, 3, 4, 5], 3)) == [3, 4, 5, 1, 2]
    assert list(rotate_list([1, 2, 3, 4, 5], 4)) == [2, 3, 4, 5, 1]
    assert list(rotate_list([1, 2, 3, 4, 5], 5)) == [1, 2, 3, 4, 5]
    assert list(rotate_list([], 3)) == []


if __name__ == "__main__":
    _run_tests()

    # do not modify below this line
    print(rotate_list([1, 2, 3, 4, 5], 0))
    print(rotate_list([1, 2, 3, 4, 5], 1))
    print(rotate_list([1, 2, 3, 4, 5], 2))
    print(rotate_list([1, 2, 3, 4, 5], 3))
    print(rotate_list([1, 2, 3, 4, 5], 4))
    print(rotate_list([1, 2, 3, 4, 5], 5))
