"""
219.63. Unique Paths II
不同路径 II

A robot is located at the top-left corner of a m x n grid (marked 'Start' in the diagram below).

The robot can only move either down or right at any point in time. The robot is trying to reach the bottom-right corner of the grid (marked 'Finish' in the diagram below).

Now consider if some obstacles are added to the grids. How many unique paths would there be?



An obstacle and empty space is marked as 1 and 0 respectively in the grid.

Note: m and n will be at most 100.

Example 1:

Input:
[
  [0,0,0],
  [0,1,0],
  [0,0,0]
]
Output: 2
Explanation:
There is one obstacle in the middle of the 3x3 grid above.
There are two ways to reach the bottom-right corner:
1. Right -> Right -> Down -> Down
2. Down -> Down -> Right -> Right


"""


# caikehe
# O(m*n) space
def uniquePathsWithObstacles1(self, obstacleGrid):
    if not obstacleGrid:
        return 
    r, c = len(obstacleGrid), len(obstacleGrid[0])
    dp = [[0 for _ in xrange(c)] for _ in xrange(r)]
    dp[0][0] = 1 - obstacleGrid[0][0]
    for i in xrange(1, r):
        dp[i][0] = dp[i-1][0] * (1 - obstacleGrid[i][0])
    for i in xrange(1, c):
        dp[0][i] = dp[0][i-1] * (1 - obstacleGrid[0][i])
    for i in xrange(1, r):
        for j in xrange(1, c):
            dp[i][j] = (dp[i][j-1] + dp[i-1][j]) * (1 - obstacleGrid[i][j])
    return dp[-1][-1]


# O(n) space
def uniquePathsWithObstacles2(self, obstacleGrid):
    if not obstacleGrid:
        return 
    r, c = len(obstacleGrid), len(obstacleGrid[0])
    cur = [0] * c
    cur[0] = 1 - obstacleGrid[0][0]
    for i in xrange(1, c):
        cur[i] = cur[i-1] * (1 - obstacleGrid[0][i])
    for i in xrange(1, r):
        cur[0] *= (1 - obstacleGrid[i][0])
        for j in xrange(1, c):
            cur[j] = (cur[j-1] + cur[j]) * (1 - obstacleGrid[i][j])
    return cur[-1]


# in place
def uniquePathsWithObstacles(self, obstacleGrid):
    if not obstacleGrid:
        return 
    r, c = len(obstacleGrid), len(obstacleGrid[0])
    obstacleGrid[0][0] = 1 - obstacleGrid[0][0]
    for i in xrange(1, r):
        obstacleGrid[i][0] = obstacleGrid[i-1][0] * (1 - obstacleGrid[i][0])
    for i in xrange(1, c):
        obstacleGrid[0][i] = obstacleGrid[0][i-1] * (1 - obstacleGrid[0][i])
    for i in xrange(1, r):
        for j in xrange(1, c):
            obstacleGrid[i][j] = (obstacleGrid[i-1][j] + obstacleGrid[i][j-1]) * (1 - obstacleGrid[i][j])
    return obstacleGrid[-1][-1]





def uniquePathsWithObstaclesMemoization(arr, row, col):
    if arr[row][col] == 1:
        return 0
    elif row == len(arr) - 1 and col == len(arr[0]) - 1:
        return 1
    elif memoize[row][col] != None:
        return memoize[row][col]
    else:
        new_row = row + 1
        new_col = col + 1
        way = 0
        if 0 <= new_row <= len(arr) - 1:
            way += uniquePathsWithObstaclesMemoization(arr, new_row, col)
        if 0 <= new_col <= len(arr[0]) - 1:
            way += uniquePathsWithObstaclesMemoization(arr, row, new_col)
        
        memoize[row][col] = way
        return memoize[row][col]


def uniquePathsWithObstacles(self, b):
	return uniquePathsWithObstaclesTabulation(obstacleGrid, len(obstacleGrid), len(obstacleGrid[0]))


def uniquePathsWithObstaclesRecursive(arr, row, col):
    if row == len(arr) - 1 and col == len(arr[0]) - 1:
        return 1
    elif arr[row][col] == 1:
        return 0
    else:
        new_row = row + 1
        new_col = col + 1
        way = 0
        if 0 <= new_row <= len(arr) - 1:
            way += uniquePathsWithObstaclesRecursive(arr, new_row, col)
        if 0 <= new_col <= len(arr[0]) - 1:
            way += uniquePathsWithObstaclesRecursive(arr, row, new_col)
        return way



                

def uniquePathsWithObstacles(self, b):
    if not b or not b[0] or b[0][0] or b[~0][~0]: return 0
    m, n = len(b), len(b[0])
    if m == 1 and n == 1: return 1
    d = {}

    def df(x, y):
        if (x, y) in d: return d[(x,y)]
        if x == m or y == n or b[x][y] == 1: return 0
        if x == m - 1 and y == n - 1: return 1
        d[(x,y)] = df(x, y + 1) + df(x + 1, y)
        return d[(x, y)]

    return df(0, 1) + df(1, 0)  



def uniquePathsWithObstacles(self, obstacleGrid):
    """
    brute force, bottom-up recursively with memorization
    - intuitively go through all the path with i+1 OR j+1
    - count the path which reaches to the destination coordinate (m, n)
    - cache the count of the coordinates which we have calculated before
    - if the current grid, grid[i][j], is blocked, tell its parent that this way is blocked by return 0
    - sum up all the coordinates' count

    Time    O(row*col) since we cache the intermediate coordinates, we wont go through the visited coordinates again
    Space   O(row*col) depth of recursions
    """
    if len(obstacleGrid) == 0 or len(obstacleGrid[0]) == 0:
        return 0
    seen = {}
    return self.dfs(obstacleGrid, 0, 0, len(obstacleGrid)-1, len(obstacleGrid[0])-1, seen)

def dfs(self, grid, i, j, m, n, seen):
    key = str(i)+","+str(j)
    if key in seen:
        return seen[key]
    if i == m and j == n:
        if grid[i][j] == 1:
            return 0
        return 1
    elif i > m or j > n:
        return 0
    if grid[i][j] == 1:
        seen[key] = 0
        return 0
    left = self.dfs(grid, i+1, j, m, n, seen)
    right = self.dfs(grid, i, j+1, m, n, seen)
    seen[key] = left + right
    return left + right



"""
public int uniquePathsWithObstacles(int[][] obstacleGrid) {
        return helper(obstacleGrid, 0, 0, new HashMap<String, Integer>());
    }

    public static int helper(int[][] obstacleGrid, int down, int right, Map<String, Integer> map) {
        String key = down + "and" + right;
        int result = 0;
        if (map.containsKey(key))
            return map.get(key);
        if (obstacleGrid[down][right] == 1) {
            result = 0;
            map.put(key, result);
            return result;
        }
        if (right == obstacleGrid[0].length - 1 && down == obstacleGrid.length - 1) {
            if (obstacleGrid[down][right] == 1) {
                result = 0;
            } else {
                result = 1;
            }
            map.put(key, result);
            return result;
        }
        if (right == obstacleGrid[0].length - 1 || down == obstacleGrid.length - 1) {
            if (right == obstacleGrid[0].length - 1) {
                result = helper(obstacleGrid, down + 1, right, map);
            } else {
                result = helper(obstacleGrid, down, right + 1, map);
            }
            map.put(key, result);
            return result;
        }
        result = helper(obstacleGrid, down, right + 1, map) + helper(obstacleGrid, down + 1, right, map);
        map.put(key, result);
        return result;
    }

"""


def uniquePathsWithObstacles(self, o: List[List[int]]) -> int:
    @functools.lru_cache(None)
    def dp(i,j):
        if o[i][j]==1: return 0
        if i==0 and j==0: return 1
        if i==0: return dp(0,j-1)
        if j==0: return dp(i-1,0)
        return dp(i-1,j) + dp(i,j-1)

    return dp(len(o)-1,len(o[0])-1)



from functools import lru_cache
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
        M, N = len(obstacleGrid), len(obstacleGrid[0])
        
        @lru_cache(maxsize=None)
        def dfs(i, j):
            if obstacleGrid[i][j]:      # hit an obstacle
                return 0
            if i == M-1 and j == N-1:   # reach the end
                return 1
            count = 0
            if i < M-1:
                count += dfs(i+1, j)    # go down
            if j < N-1:
                count += dfs(i, j+1)    # go right
            return count
        
        return dfs(0, 0)




def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
    #新建矩阵版
    height, width = len(obstacleGrid),len(obstacleGrid[0])
    store = [[0]*width for i in range(height)]

    #从上到下，从左到右
    for m in range(height):#每一行
        for n in range(width):#每一列
            if not obstacleGrid[m][n]: #如果这一格没有障碍物
                if m == n == 0: #或if not(m or n)
                    store[m][n] = 1
                 else:
                    a = store[m-1][n] if m!=0 else 0 #上方格子
                    b = store[m][n-1] if n!=0 else 0 #左方格子
                    store[m][n] = a+b
    return store[-1][-1]




 def uniquePathsWithObstaclesTabulation(arr, row, col):
    table = [[0 for _ in range(col + 1)] for _ in range(row + 1)]
    
    for i in range(row):
        for j in range(col):
            if arr[i][j] == 1:
                table[i][j] = 0
            elif i == 0 and j == 0:
                table[i][j] = 1
            else:
                table[i][j] = table[i][j - 1] + table[i - 1][j]

    return table[row - 1][col - 1]



def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
    #原矩阵版
    height, width = len(obstacleGrid),len(obstacleGrid[0])

    #从上到下，从左到右
    for m in range(height):#每一行
        for n in range(width):#每一列
            if obstacleGrid[m][n]: #如果这一格有障碍物
                obstacleGrid[m][n] = 0
            else:
                if m == n == 0: #或if not(m or n)
                    obstacleGrid[m][n] = 1
                else:
                    a = obstacleGrid[m-1][n] if m!=0 else 0 #上方格子
                    b = obstacleGrid[m][n-1] if n!=0 else 0 #左方格子
                    obstacleGrid[m][n] = a+b
    return obstacleGrid[-1][-1]




	m = obstacleGrid
    if not m or m == [[]] or len(m)==0 or m[0][0] == 1:
        return 0
    
    # start:
    m[0][0] = 1
    
    # top row:
    for i in range(1, len(m[0])):
        if m[0][i] == 1: # obstacle
            m[0][i] = 0
        else:
            m[0][i] = m[0][i-1] # previous cell (cell to the left)
            
    # left most col:
    for i in range(1, len(m)):
        if m[i][0] == 1: # obstacle
            m[i][0] = 0
        else:
            m[i][0] = m[i-1][0] # previous cell (cell to the top)
            
    # rest of the grid:
    for i in range(1, len(m)):
        for j in range(1, len(m[0])):
            if m[i][j] == 1:
                m[i][j] = 0
            else:
                m[i][j] = m[i-1][j] + m[i][j-1]
                
    return m[len(m)-1][len(m[0])-1]



def uniquePathsWithObstacles(self, obstacleGrid):
    if (not obstacleGrid) or obstacleGrid[0][0]:
        return 0
    
    obstacleGrid[0][0] = 1
    m, n = len(obstacleGrid), len(obstacleGrid[0])
    
    for i in range(1,m):
        obstacleGrid[i][0] = obstacleGrid[i-1][0] * (1-obstacleGrid[i][0])
        
    for j in range(1,n):
        obstacleGrid[0][j] = obstacleGrid[0][j-1] * (1-obstacleGrid[0][j])
        
    for i in range(1,m):
        for j in range(1,n):
            obstacleGrid[i][j] = (1-obstacleGrid[i][j])*(obstacleGrid[i-1][j]+obstacleGrid[i][j-1])
    
    return obstacleGrid[-1][-1]












































































