import math

def matching_pairs_1(s, t):
    # Write your code here
    N = len(t)
    baseline_matches = [int(s[i] == t[i]) for i in range(N)]
    delta = [[0] * N for j in range(N)]

    def get_match_delta_rc(baseline, s, t, i, j):
        """return swap score from two elements"""
        return -baseline[i] + int(s[i] == t[j]) - baseline[j] + int(s[j] == t[i])

    running_max = -math.inf
    for row in range(N):
        for col in range(N):
            if row != col:
                delta[row][col] = get_match_delta_rc(baseline_matches, s, t, row, col)
                if running_max < delta[row][col]:
                    running_max = delta[row][col]
                    max_row, max_col = row, col

    return sum(baseline_matches) + delta[max_row][max_col]


def matching_pairs(s, t):
    # Write your code here
    N = len(t)
    baseline_matches = [int(s[i] == t[i]) for i in range(N)]

    # delta = [[0]*N for j in range(N)]

    def get_match_delta_rc(baseline, s, t, i, j):
        """return swap score from two elements"""
        return -baseline[i] + int(s[i] == t[j]) - baseline[j] + int(s[j] == t[i])

    running_max = -math.inf
    for row in range(N):
        for col in range(N):
            if row != col:
                # delta[row][col] = get_match_delta_rc(baseline_matches, s, t, row, col)
                curr_delta = get_match_delta_rc(baseline_matches, s, t, row, col)
                if running_max < curr_delta:
                    running_max = curr_delta
                    max_row, max_col = row, col

    return sum(baseline_matches) + running_max


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


if __name__ == "__main__":
  s_1, t_1 = "abcde", "adcbe"
  expected_1 = 5
  output_1 = matching_pairs(s_1, t_1)
  check(expected_1, output_1)

  s_2, t_2 = "abcd", "abcd"
  expected_2 = 2
  output_2 = matching_pairs(s_2, t_2)
  check(expected_2, output_2)