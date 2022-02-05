import math
from FB.checker import Checker

problem = Checker()


# %% test grounds

# %%
def can_change_Rec(targetMoney, denominations):
    # Write your code here
    if 1 in denominations and targetMoney > 0:
        return True
    if 2 in denominations and targetMoney > 0 and targetMoney % 2 == 0:
        return True
    # optimizing for target being multiple of some number
    # for gcd in reversed(range(3, int(math.sqrt(targetMoney)))):
    change_computed = {}

    def exactRecursive(money, denominations):

        if money == 0:
            return True

        # global change_computed
        cc = change_computed

        if money in cc:  # memo
            return cc[money]

        else:
            # calculated non-cached
            if all([d > money for d in denominations]):
                return False

            # now reducing problem
            sub_cases = []
            for coin in denominations:
                if money >= coin:
                    sub_cases.append(exactRecursive(money - coin, denominations))
            cc[money] = any(sub_cases)

        return cc[money]

    return exactRecursive(targetMoney, denominations)


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
    return 1 if ways[amount] > 0 else -1


# %%
def printInteger(n):
    print('[', n, ']', sep='', end='')


test_case_number = 1


def check(expected, output):
    global test_case_number
    result = False
    if expected == output:
        result = True
    rightTick = '\u2713'
    wrongTick = '\u2717'
    if result:
        print(rightTick, 'Test #', test_case_number, sep='')
    else:
        print(wrongTick, 'Test #', test_case_number, ': Expected ', sep='', end='')
        printInteger(expected)
        print(' Your output: ', end='')
        printInteger(output)
        print()
    test_case_number += 1


# %%
target_1 = 94
arr_1 = [5, 10, 25, 100, 200]
expected_1 = False
output_1 = canGetExactChange(target_1, arr_1)
check(expected_1, output_1)

target_2 = 75
arr_2 = [4, 17, 29]
expected_2 = True
output_2 = canGetExactChange(target_2, arr_2)
check(expected_2, output_2)
