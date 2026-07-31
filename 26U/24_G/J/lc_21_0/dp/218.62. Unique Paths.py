"""
218.62. Unique Paths
不同路径


A robot is located at the top-left corner of a m x n grid (marked 'Start' in the diagram below).

The robot can only move either down or right at any point in time. The robot is trying 
to reach the bottom-right corner of the grid (marked 'Finish' in the diagram below).

How many possible unique paths are there?


Above is a 7 x 3 grid. How many possible unique paths are there?

 

Example 1:

Input: m = 3, n = 2
Output: 3
Explanation:
From the top-left corner, there are a total of 3 ways to reach the bottom-right corner:
1. Right -> Right -> Down
2. Right -> Down -> Right
3. Down -> Right -> Right
Example 2:

Input: m = 7, n = 3
Output: 28
 

Constraints:

1 <= m, n <= 100
It's guaranteed that the answer will be less than or equal to 2 * 10 ^ 9.


"""

def uniquePaths(self, m: int, n: int) -> int:
    dp = [[1] * n for _ in range(m)]
    def rec(i, j):
        if i == 0 or j == 0: return 1
        if dp[i][j] != 1: 
            return dp[i][j]
        dp[i][j] = rec(i, j-1) + rec(i-1, j)
        return dp[i][j]
    return rec(m-1, n-1)




dp = [ [1] * 101 for _ in range(101)]
class Solution:
    
    def uniquePaths(self, m: int, n: int) -> int:
        if m == 1 or n == 1: return 1
        if dp[m][n] != 1: return dp[m][n]
        dp[m-1][n] = self.uniquePaths(m-1, n)
        dp[m][n-1] = self.uniquePaths(m, n-1)
        dp[m][n] = dp[m-1][n] + dp[m][n-1]
        return dp[m][n]



"""
def uniquePaths(self, m: int, n: int) -> int:
    cur = [1] * n
    for j in range(1, m):
        for i in range(n):
            if i == 0:
                continue
            else:
                cur[i] += cur[i-1]
    return cur[-1]
"""



def uniquePaths(self, m: int, n: int) -> int:
    cur = [1] * n
    for i in range(1, m):
        for j in range(1, n):
            cur[j] += cur[j-1]
    return cur[-1]



def uniquePaths(self, m: int, n: int) -> int:
    pre = [1] * n
    cur = [1] * n
    for i in range(1, m):
        for j in range(1, n):
            cur[j] = pre[j] + cur[j-1]
        pre = cur[:]
    return pre[-1]





# rec

def uniquePaths(self, m: int, n: int) -> int:
    def rec(n, m):
        if n == 0 or m == 0: return 1
        return rec(n-1, m ) + rec(n, m-1)
    return rec(n-1, m-1)





def uniquePaths(self, m, n):
        cache = {}
        return self.findPath(m, n, cache)

def findPath(self, m, n, cache):
    if (m, n) in cache:
        return cache[(m, n)]
    elif m == 1 or n == 1:
        return 1

    cache[(m, n)] = self.findPath(m - 1, n, cache) + self.findPath(m, n - 1, cache)
    return cache[(m, n)]



from functools import lru_cache
class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
	
        @lru_cache(None)
        def fn(i, j):
            if not i or not j: return 1
            return fn(i-1, j) + fn(i, j-1)
			
        return fn(m-1, n-1)



def uniquePaths(self, m: int, n: int) -> int:
    memo = dict()        
    
    def fn(i, j):
        if (i, j) in memo: return memo[i, j]
        if i == 0 or j == 0: memo[i, j] = 1
        else: memo[i, j] = fn(i-1, j) + fn(i, j-1)
        return memo[i, j]
    
    return fn(m-1, n-1)



def uniquePaths(self, m: int, n: int) -> int:
    def fn(i, j, memo={}):
        if (i, j) in memo: return memo[i, j]
        if i == 0 or j == 0: memo[i, j] = 1
        else: memo[i, j] = fn(i-1, j, memo) + fn(i, j-1, memo)
        return memo[i, j]
    
    return fn(m-1, n-1)



def uniquePaths(self, m: int, n: int) -> int: 
    def choose(n, k):
        k = min(k, n-k)
        ans = 1
        for i in range(k):
            ans *= n-i
            ans //= i+1
        return ans 
    return choose(m+n-2, m-1)





def helper(self, i, j, m, n, paths):
    if 0<=i<m and 0<=j<n:
        if paths[i][j] != -1:
            return paths[i][j]
        paths[i][j] = self.helper(i, j+1, m, n, paths) + self.helper(i+1, j, m, n, paths)
        return paths[i][j]
    return 0

def uniquePaths(self, m, n):
    if m == 0 or n == 0:
        return 0
    paths = [[-1]*n for _ in range(m)]
    paths[m-1][n-1] = 1
    return self.helper(0, 0, m, n, paths)
































































































