# %%
from functools import lru_cache
from typing import Tuple, List



@lru_cache(maxsize=1024)
def num_ways(amount: int, coins: Tuple[int, ...], i: int = 0) -> int:
    if amount == 0:
        return 1
    if amount < 0 or i == len(coins):
        return 0

    # either use coins[i], or skip it
    return num_ways(amount - coins[i], coins, i) + num_ways(amount, coins, i + 1)

# %%
import pytest
@pytest.mark.parametrize("amount,coins,expected", [
    (4, (1, 2, 3), 4),
    (10, (10,), 1),
    (500, tuple([3,5,7,8,9,10,11]), 35502874),
]) 
def test_change(amount, coins, expected):
    assert Solution().change(amount, coins) == expected

    # raise SystemExit(pytest.main([__file__, "-v"]))

#%% 
class Solution:
    def change(self, amount: int, coins: List[int]) -> int:
        return num_ways(amount, tuple(sorted(coins)))


if __name__ == '__main__':
    # case0 =  num_ways(4, (1, 2, 3))
    # exit(0)
    # 

    raise SystemExit(pytest.main([__file__, "-v"]))
# %%
