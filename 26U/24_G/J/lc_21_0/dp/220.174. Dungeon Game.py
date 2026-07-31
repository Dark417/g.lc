"""
220.174. Dungeon Game
地下城游戏



The demons had captured the princess (P) and imprisoned her in the bottom-right corner 
of a dungeon. The dungeon consists of M x N rooms laid out in a 2D grid. Our valiant 
knight (K) was initially positioned in the top-left room and must fight his way through 
the dungeon to rescue the princess.

The knight has an initial health point represented by a positive integer. If at any 
point his health point drops to 0 or below, he dies immediately.

Some of the rooms are guarded by demons, so the knight loses health (negative integers) 
upon entering these rooms; other rooms are either empty (0's) or contain magic orbs that increase the knight's health (positive integers).

In order to reach the princess as quickly as possible, the knight decides to move only 
rightward or downward in each step.

 

Write a function to determine the knight's minimum initial health so that he is able 
to rescue the princess.

For example, given the dungeon below, the initial health of the knight must be at least 
7 if he follows the optimal path RIGHT-> RIGHT -> DOWN -> DOWN.

-2 (K)	-3	3
-5	-10	1
10	30	-5 (P)
 

Note:

The knight's health has no upper bound.
Any room can contain threats or power-ups, even the first room the knight enters and 
the bottom-right room where the princess is imprisoned.

"""


def calculateMinimumHP(self, dungeon: List[List[int]]) -> int:
    n, m = len(dungeon), len(dungeon[0])
    BIG = 10**9
    dp = [[BIG] * (m + 1) for _ in range(n + 1)]
    dp[n][m - 1] = dp[n - 1][m] = 1
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            minn = min(dp[i + 1][j], dp[i][j + 1])
            dp[i][j] = max(minn - dungeon[i][j], 1)

    return dp[0][0]


def calculateMinimumHP(self, dungeon):
    m, n = len(dungeon), len(dungeon[0])
    dp = [[float("inf")]*(n+1) for _ in range(m+1)]
    dp[m-1][n], dp[m][n-1] = 1, 1
        
    for i in range(m-1,-1,-1):
        for j in range(n-1,-1,-1):
            dp[i][j] = max(min(dp[i+1][j],dp[i][j+1])-dungeon[i][j],1)
    
    return dp[0][0]



def calculateMinimumHP(self, dungeon):
    n = len(dungeon[0])
    need = [2**31] * (n-1) + [1]
    for row in dungeon[::-1]:
        for j in range(n)[::-1]:
            need[j] = max(min(need[j:j+2]) - row[j], 1)
    return need[0]



def calculateMinimumHP(self, dungeon):
    @functools.lru_cache(None)
    def dp(i,j):
        if (i,j) in ((m-1,n),(m,n-1)): return 1
        if i == m or j == n: return math.inf
        return max(min(dp(i+1,j),dp(i,j+1))-dungeon[i][j],1)

    m, n = len(dungeon), len(dungeon[0])
    return dp(0,0)



# O(m*n) space
def calculateMinimumHP1(self, dungeon):
    if not dungeon:
        return 
    r, c = len(dungeon), len(dungeon[0])
    dp = [[0 for _ in xrange(c)] for _ in xrange(r)]
    dp[-1][-1] = max(1, 1-dungeon[-1][-1])
    for i in xrange(c-2, -1, -1):
        dp[-1][i] = max(1, dp[-1][i+1]-dungeon[-1][i])
    for i in xrange(r-2, -1, -1):
        dp[i][-1] = max(1, dp[i+1][-1]-dungeon[i][-1])
    for i in xrange(r-2, -1, -1):
        for j in xrange(c-2, -1, -1):
            dp[i][j] = max(1, min(dp[i+1][j], dp[i][j+1])-dungeon[i][j])
    return dp[0][0]
    
# O(n) space
def calculateMinimumHP(self, dungeon):
    if not dungeon:
        return 
    r, c = len(dungeon), len(dungeon[0])
    dp = [0 for _ in xrange(c)]
    dp[-1] = max(1, 1-dungeon[-1][-1])
    for i in xrange(c-2, -1, -1):
        dp[i] = max(1, dp[i+1]-dungeon[-1][i])
    for i in xrange(r-2, -1, -1):
        dp[-1] = max(1, dp[-1]-dungeon[i][-1])
        for j in xrange(c-2, -1, -1):
            dp[j] = max(1, min(dp[j], dp[j+1])-dungeon[i][j])
    return dp[0]




"""
public int calculateMinimumHP(int[][] dungeon) {
        return dfs(dungeon, dungeon.length, dungeon[0].length, 0, 0);
    }

    private int dfs(int[][] dungeon, int m, int n, int i, int j) {
        // 到达终点，递归终止。
        if (i == m - 1 && j == n - 1) {
            return Math.max(1 - dungeon[i][j], 1);
        }
        // 最后一行，只能向右搜索。
        if (i == m - 1) {
            return Math.max(dfs(dungeon, m, n, i, j + 1) - dungeon[i][j], 1);
        }
        // 最后一列，只能向下搜索。
        if (j == n - 1) {
           return Math.max(dfs(dungeon, m, n, i + 1, j) - dungeon[i][j], 1);
        }
        // 向下搜索 + 向右搜索，得到(i, j)点的后续路径所要求的最低血量 Math.min(dfs(i + 1, j), dfs(i, j + 1))，
        // 又因为(i, j)点本身提供血量dungeon[i][j], 因此从(i, j)开始所需的最低血量为 Math.min(dfs(i + 1, j), dfs(i, j + 1)) - dungeon[i][j]
        // 因为骑士的血量不能小于1，因此要和1取个max。
        return Math.max(Math.min(dfs(dungeon, m, n, i + 1, j), dfs(dungeon, m, n, i, j + 1)) - dungeon[i][j], 1);
    }

"""






























































































