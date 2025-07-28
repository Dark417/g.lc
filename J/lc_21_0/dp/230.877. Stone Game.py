"""
230.877. Stone Game
石子游戏


Alex and Lee play a game with piles of stones.  There are an even number of piles 
arranged in a row, and each pile has a positive integer number of stones piles[i].

The objective of the game is to end with the most stones.  The total number of stones is odd, so there are no ties.

Alex and Lee take turns, with Alex starting first.  Each turn, a player takes the entire pile of 
stones from either the beginning or the end of the row.  This continues until there 
are no more piles left, at which point the person with the most stones wins.

Assuming Alex and Lee play optimally, return True if and only if Alex wins the game.

 

Example 1:

Input: [5,3,4,5]
Output: true
Explanation: 
Alex starts first, and can only take the first 5 or the last 5.
Say he takes the first 5, so that the row becomes [3, 4, 5].
If Lee takes 3, then the board is [4, 5], and Alex takes 5 to win with 10 points.
If Lee takes the last 5, then the board is [3, 4], and Alex takes 4 to win with 9 points.
This demonstrated that taking the first 5 was a winning move for Alex, so we return true.
 

Note:

2 <= piles.length <= 500
piles.length is even.
1 <= piles[i] <= 500
sum(piles) is odd.

"""


# lee 
def stoneGame(self, p):
    n = len(p)
    dp = [[0] * n for i in range(n)]
    for i in range(n): dp[i][i] = p[i]
    for d in range(1, n):
        for i in range(n - d):
            dp[i][i + d] = max(p[i] - dp[i + 1][i + d], p[i + d] - dp[i][i + d - 1])
    return dp[0][-1] > 0



def stoneGame(self, p):
    n = len(p)
    dp = p[:]
    for d in range(1, n):
        for i in range(n - d):
            dp[i] = max(p[i] - dp[i + 1], p[i + d] - dp[i])
    return dp[0] > 0



# official
from functools import lru_cache

class Solution:
    def stoneGame(self, piles):
        N = len(piles)

        @lru_cache(None)
        def dp(i, j):
            # The value of the game [piles[i], piles[i+1], ..., piles[j]].
            if i > j: return 0
            parity = (j - i - N) % 2
            if parity == 1:  # first player
                return max(piles[i] + dp(i+1,j), piles[j] + dp(i,j-1))
            else:
                return min(-piles[i] + dp(i+1,j), -piles[j] + dp(i,j-1))

        return dp(0, N - 1) > 0



def stoneGame(self, piles: List[int]) -> bool:
    n = len(piles)
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = piles[i]
    for j in range(1,n):
        for i in range(j-1, -1, -1):
            dp[i][j] = max(piles[i] - dp[i + 1][j], piles[j] - dp[i][j - 1])
    return dp[0][n-1]>0



def stoneGame(piles):
	cache = {}
	piles = tuple(piles)
	def firstscore(i,j):
		if i>=j: return 0
		if j==i+1 and j < len(piles): return piles[i]
		if (i,j) in cache: return cache[i,j]
		res = max(piles[i]+min(firstscore(i+2,j), firstscore(i+1,j-1)) , piles[j-1] + min(firstscore(i+1,j-1), firstscore(i,j-2)))
		cache[i,j] = res
		return res
	
	Alex = firstscore(0,len(piles))
	Lee = sum(piles) - Alex
	return Alex > Lee



def stoneGame(self, piles):
    def helper(i,j, me, other):
        if i > j:
            return me < other
        else:
            key = (i,j,me,other)
            if key in table:
                return table[key]
            ans =  helper(i+1,j, other, me + piles[i]) or helper(i,j-1, other, me + piles[j])
            table[key] = ans
            return ans
    table = {}
    return helper(0, len(piles)-1, 0, 0)



def stoneGame(self, piles):
    def pmin(i, j):
        if (i,j) in mincache: return mincache[(i,j)]
        if i == j: return 0
        mincache[(i,j)] =  min(pmax(i+1, j), pmax(i, j-1))
        return mincache[(i,j)]

    def pmax(i, j):
        if (i,j) in maxcache: return maxcache[(i,j)]
        if i == j: return piles[i]
        maxcache[(i,j)] =  max(piles[i] + pmin(i+1, j), pmin(i, j-1) + piles[j])
        return maxcache[(i,j)]

    mincache, maxcache = {}, {}
    p1 = pmax(0, len(piles)-1)
    p2 = sum(piles) - p1
    return p1 > p2




def stoneGame(self, piles: List[int]) -> bool:
    dp =[[0]*len(piles) for _ in range(len(piles))]
    
    for i in range(len(piles)-1,-1,-1):
        for j in range(i+1,len(piles),2): # j>i and (j-i+1) is even | make it faster
            if i+1==j:
                dp[i][j] = max(piles[i],piles[j])
            else:
                dp[i][j] = max(piles[i] + min(dp[i+2][j],dp[i+1][j-1]), piles[j] + min(dp[i+1][j-1],dp[i][j-2]))
         
    return dp[0][-1] > sum(piles) - dp[0][-1]





def stoneGame(self, piles):
    n = len(piles)
    dp = [[0]*n for _ in range(n)]
    for i in range(n-1,-1,-1):
        for j in range(i,n):
            if (n - (j-i+1) ) % 2 == 0:
                dp[i][j] = max((dp[i][j-1] if j > 0 else 0)+piles[j],(dp[i+1][j] if i < n-1 else 0 )+piles[i])
            else:
                dp[i][j] = min((dp[i][j-1] if j > 0 else 0)-piles[j],(dp[i+1][j] if i < n-1 else 0 )-piles[i])
    return dp[0][-1] > 0








































