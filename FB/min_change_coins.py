# %%
from FB.checker import Checker

problem = Checker()


# %%
def min_change(coins, amount):
    if amount == 0:
        return 0

    ways = [0] * (amount + 1)
    ways[0] = 0

    for c in reversed(sorted(coins)):
        if amount >= c:
            ways[c] = 1
        for idx in range(c + 1, amount + 1):
            w = ways[idx]
            if ways[idx - c] > 0:
                if w > 0:
                    ways[idx] = min(w, 1 + ways[idx - c])
                else:
                    ways[idx] = 1 + ways[idx - c]
            # print([v-1 if v>0 else 0 for v in ways])
        # print(ways)
    return ways[amount] if ways[amount] > 0 else -1


# %%
problem.check(3, min_change([1, 2, 5], 11))
problem.check(3, min_change([1, 2, 5], 9))