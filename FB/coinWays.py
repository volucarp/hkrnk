# %% test Zone
from itertools import permutations

amount = 11
coins = [2, 4, 6]

combinations = []
for c in coins:
    combinations.append([c * i for i in range(amount // c)])

[i for i in permutations(*combinations)]


# %% Solutions zone
class Solution(object):
    test_case_number = 1

    @staticmethod
    def printInteger(n):
        print('[', n, ']', sep='', end='')

    def check(self, expected, output):

        result = False
        if expected == output:
            result = True
        rightTick = '\u2713'
        wrongTick = '\u2717'
        if result:
            print(rightTick, 'Test #', self.test_case_number, sep='')
        else:
            print(wrongTick, 'Test #', self.test_case_number, ': Expected ', sep='', end='')
            self.printInteger(expected)
            print(' Your output: ', end='')
            self.printInteger(output)
            print()
        self.test_case_number += 1

prob = Solution()

def getNumberOfWays(N, Coins):
    # Create the ways array to 1 plus the amount
    # to stop overflow
    ways = [0] * (N + 1)

    # Set the first way to 1 because its 0 and
    # there is 1 way to make 0 with 0 coins
    ways[0] = 1

    # Go through all of the coins
    for i in range(len(Coins)):

        # Make a comparison to each index value
        # of ways with the coin value.
        for j in range(len(ways)):
            if Coins[i] <= j:
                # Update the ways array
                ways[j] += ways[int(j - Coins[i])]

                # return the value at the Nth position
    # of the ways array.
    return ways[N]


def printArray(coins):
    for i in coins:
        print(i)


def coin_change_ans(coins, amount):
    if amount == 0:
        return 0
    ways = [0 for i in range(amount + 1)]
    ways[0] = 1
    curr_sum = 0

    for c in sorted(coins):
        for w in range(len(ways)):
            if w >= c:
                ways[w] += ways[w - c]
        print(ways)

    return ways[amount]


# %% testing zone

prob.check(3, coin_change_ans([2, 5], 11))

# %% check internet prob
prob.check(3, getNumberOfWays(11, [1, 2, 5]))

# %%
print(getNumberOfWays(12, [2, 4, 8]))
print(getNumberOfWays(11, [3, 5, 10]))
print(getNumberOfWays(11, [1, 2, 5]))
print(getNumberOfWays(5, [3, 4]))


