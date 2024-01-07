#%%
import math

def perms(n):
  return n*(n-1)/2

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

#%%
# Add any helper functions you may need here
def perms_math(n):
    return float(n/2) * (n - 1)

def perms(n):
    result = 0
    return(sum(range(n)))

def perms_eval(n):
    return(eval("{}*{}/2".format(n, n-1)))

def numberOfWays(arr, k):
    # Write your code here
    occurances = {}
    used = {}
    for element in arr:
        occurances[element] = occurances.get(element, 0) + 1
    #print("debug: occ_arr {}".format(occurances))

    ways = 0
    for el, countof in occurances.items():
        if k == el * 2:
            ways += perms(occurances[el])
        else:
            ways += countof * occurances.get(k - el, 0) * used.get(k - el, 1)
        used[el] = 0
        used[k - el] = 0

    return ways

print(perms_math(10))
print(perms_eval(10))
print(perms(10))
#%%
k_1 = 6
arr_1 = [1, 2, 3, 4, 3]
expected_1 = 2
output_1 = numberOfWays(arr_1, k_1)
check(expected_1, output_1)

k_2 = 6
arr_2 = [1, 5, 3, 3, 3]
expected_2 = 4
output_2 = numberOfWays(arr_2, k_2)
check(expected_2, output_2)

# Add your own test cases here
arr_3 = [4, 4, 4, 4]
k_3 = 8
output_3 = numberOfWays(arr_3, k_3)
check(6, output_3)

arr_4 = [int(1e9)] * 100000
k_4 = 2 * int(1e9)
check(49999400001, numberOfWays(arr_4, k_4))

arr_5 = [1] + [int(1e9)] * 100000 + [99999]
k_5 = int(1e5)
check(1, numberOfWays(arr_5, k_5))