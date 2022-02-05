#%% load checker
class Checker(object):
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

# %%
