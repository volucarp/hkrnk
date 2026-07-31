import pytest
from max_substring import CharSubsequence



@pytest.mark.parametrize("a,b,expected", [
    ("oxcpqrsvwf", "shmtulqrypy", 2),
    ("a"*200, "a"*200, 200),
])
def test_subsequence(a, b, expected):
    assert CharSubsequence().longestCommonSubsequence(a, b) == expected


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, "-v"])) 