import math

#%% test grounds
arr = [5, 10, 6, 8]
arr.sort()


#%%
def minOverallAwkwardness(arr):
  """return min diff in arranged circular sitting"""

  N = len(arr)
  arr.sort()
  prev_L_guest = arr[0]
  prev_R_guest = arr[0]
  max_diff = 0
  if N< 2:
    return 0
  for i in range( 1, N):
      #print(arr[i])
      if i%2 == 1: #Left cases
          max_diff = max(max_diff, arr[i] - prev_L_guest)
          prev_L_guest = arr[i]
      else:
          max_diff = max(max_diff, arr[i] - prev_R_guest)
          prev_R_guest = arr[i]
  max_diff = max(max_diff, arr[i]-arr[i-1])
  #TODO: Check N=1, 2, 3
  return max_diff

#%%
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
arr_1 = [5, 10, 6, 8]
expected_1 = 4
output_1 = minOverallAwkwardness(arr_1)
check(expected_1, output_1)

arr_2 = [1, 2, 5, 3, 7]
expected_2 = 4
output_2 = minOverallAwkwardness(arr_2)
check(expected_2, output_2)



#%%
if __name__ == "__main__":
  arr_1 = [5, 10, 6, 8]
  expected_1 = 4
  output_1 = minOverallAwkwardness(arr_1)
  check(expected_1, output_1)

  arr_2 = [1, 2, 5, 3, 7]
  expected_2 = 4
  output_2 = minOverallAwkwardness(arr_2)
  check(expected_2, output_2)