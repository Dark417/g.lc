# 516. 最长回文子序列


def longestPalindromeSubseq(self, s: str) -> int:
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]

a = [1,2,3]

def longestPalindromeSubseq(self, s: str) -> int:
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for j in range(n):
        dp[j][j] = 1
        for i in range(j-1, -1, -1):
            if s[i] == s[j]:
                dp[i][j] = dp[i+1][j-1] + 2
            else:
                dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    return dp[0][n-1]

        
# 将字符串翻转，然后求两个字符串的最长公共子序列
def longestPalindromeSubseq(self, s):
    n = len(s)
    dp = [[0] * (n + 1) for i in xrange(n + 1)]
    ss = s[::-1]

    for i in xrange(1, n + 1):
        for j in xrange(1, n + 1):
            if s[i - 1] == ss[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i][j - 1], dp[i - 1][j])
    
    return dp[n][n]





