"""
217.64. Minimum Path Sum
最小路径和

Given a m x n grid filled with non-negative numbers, find a path from top left to bottom 
right which minimizes the sum of all numbers along its path.

Note: You can only move either down or right at any point in time.

Example:

Input:
[
  [1,3,1],
  [1,5,1],
  [4,2,1]
]
Output: 7
Explanation: Because the path 1→3→1→1→1 minimizes the sum.


"""


def minPathSum(self, grid: List[List[int]]) -> int:
    dct = {}
    xx = len(grid)
    yy = len(grid[0])

    def dfs(x: int, y: int) -> int:
        if (x, y) in dct:
            return dct[(x, y)]
        if x == xx or y == yy:
            return float("inf")
        p = min(dfs(x+1, y), dfs(x, y+1))
        dct[(x, y)] = grid[x][y]+(0 if p == float("inf") else p)
        return dct[(x, y)]

    return dfs(0, 0)



def minPathSum(self, grid: List[List[int]]) -> int:
    x = len(grid[0])
    y = len(grid)
    for i in range(x-2, -1, -1):
        grid[-1][i] += grid[-1][i+1]
    for i in range(y-2, -1, -1):
        grid[i][-1] += grid[i+1][-1]
    for i in range(y-2, -1, -1):
        for j in range(x-2, -1, -1):
            grid[i][j] += min(grid[i][j+1], grid[i+1][j])
    return grid[0][0]


def minPathSum(self, grid: List[List[int]]) -> int:
    dct = defaultdict(lambda: float("inf"))
    xx = len(grid)
    yy = len(grid[0])
    deq = deque([(xx-1, yy-1)])
    while deq:
        x, y = deq.popleft()
        if (x, y) in dct:
            continue
        if x < 0 or y < 0:
            continue
        p = min(dct[(x+1, y)], dct[(x, y+1)])
        deq.extend([(x-1, y), (x, y-1)])
        dct[(x, y)] = grid[x][y]+(0 if p == float("inf") else p)
    return dct[(0, 0)]




def minPathSum(self, grid: List[List[int]]) -> int:
	if not grid:
	    return 0
	#数组的长和宽
	size_row,size_col = len(grid),len(grid[0])
	def helper(row,col):
	    if row >= size_row or col >= size_col:
	        return float("inf") #这里要定义一个较大的数，因为这个值会被返回到min函数中
	    #到达最后一个元素的时候结束递归
	    if row == size_row - 1 and col == size_col - 1:
	        return grid[row][col]
	    #自顶向下递归
	    return grid[row][col] + min(helper(row+1,col),helper(row,col+1))

	return helper(0,0)



def minPathSum(self, grid: List[List[int]]) -> int:
	if not grid:
	    return 0
	# 数组的长和宽
	size_row ,size_col = len(grid) ,len(grid[0])

	# 定义记忆化需要的辅助数组
	nums = [[None ] *(size_co l +1) for _ in range(size_ro w +1)]

	def helper(row ,col):
	    if row >= size_row or col >= size_col:
	        return float("inf")  # 这里要定义一个较大的数，因为这个值会被返回到min函数中
	    if row == size_row - 1 and col == size_col - 1:
	        return grid[row][col]

	    # 向下移动一步的情况
	    if nums[ro w +1][col] != None:
	        down = nums[ro w +1][col]
	    else:
	        down = helper(ro w +1 ,col)
	        nums[ro w +1][col] = down

	    # 向右移动的情况
	    if nums[row][co l +1] != None:
	        right = nums[row][co l +1]
	    else:
	        right = helper(row ,co l +1)
	        nums[row][co l +1] = right

	    return grid[row][col] + min(down ,right)

	return helper(0 ,0)






def minPathSum(self, grid: List[List[int]]) -> int:
    n = len(grid)
    m = len(grid[0])
    for i in range(n-1, -1, -1):
        for j in range(m-1, -1, -1):
            if i==n-1 and j==m-1:
                continue
            elif i==n-1 and j<m-1:
                grid[i][j] += grid[i][j+1]
            elif i<n-1 and j==m-1:
                grid[i][j] += grid[i+1][j]
            else:
                grid[i][j] += min(grid[i+1][j], grid[i][j+1])
    return grid[0][0]









def minPathSum(self, grid: [[int]]) -> int:
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if i == j == 0: continue
            elif i == 0:  grid[i][j] = grid[i][j - 1] + grid[i][j]
            elif j == 0:  grid[i][j] = grid[i - 1][j] + grid[i][j]
            else: grid[i][j] = min(grid[i - 1][j], grid[i][j - 1]) + grid[i][j]
    return grid[-1][-1]





def minPathSum(self, grid: List[List[int]]) -> int:
    if not grid or not grid[0]:
        return 0
    
    rows, columns = len(grid), len(grid[0])
    dp = [[0] * columns for _ in range(rows)]
    dp[0][0] = grid[0][0]
    for i in range(1, rows):
        dp[i][0] = dp[i - 1][0] + grid[i][0]
    for j in range(1, columns):
        dp[0][j] = dp[0][j - 1] + grid[0][j]
    for i in range(1, rows):
        for j in range(1, columns):
            dp[i][j] = min(dp[i - 1][j], dp[i][j - 1]) + grid[i][j]
    
    return dp[rows - 1][columns - 1]




def minPathSum(self, grid: List[List[int]]) -> int:
        dp = [float('inf')] * (len(grid[0])+1)
        dp[1] = 0
        for row in grid:
            for j, v in enumerate(row):
                dp[j + 1] = min(dp[j], dp[j + 1]) + v
        return dp[-1]


def minPathSum(self, grid):
    dp = [float('inf')] * (len(grid[0])+1)
    dp[1] = 0
    for row in grid:
        for idx, num in enumerate(row):
            dp[idx + 1] = min(dp[idx], dp[idx + 1]) + num
    return dp[-1]







# caikehe
# O(m*n) space
def minPathSum(self, grid):
    if not grid:
        return 
    r, c = len(grid), len(grid[0])
    dp = [[0 for _ in xrange(c)] for _ in xrange(r)]
    dp[0][0] = grid[0][0]
    for i in xrange(1, r):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    for i in xrange(1, c):
        dp[0][i] = dp[0][i-1] + grid[0][i]
    for i in xrange(1, len(grid)):
        for j in xrange(1, len(grid[0])):
            dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]
    return dp[-1][-1]
            
# O(2*n) space
def minPathSum2(self, grid):
    if not grid:
        return 
    r, c = len(grid), len(grid[0])
    pre = cur = [0] * c
    pre[0] = grid[0][0] 
    for i in xrange(1, c):
        pre[i] = pre[i-1] + grid[0][i]
    for i in xrange(1, r):
        cur[0] = pre[0] + grid[i][0]
        for j in xrange(1, c):
            cur[j] = min(cur[j-1], pre[j]) + grid[i][j]
        pre = cur
    return cur[-1]
    
# O(n) space
def minPathSum(self, grid):
    if not grid:
        return 
    r, c = len(grid), len(grid[0])
    cur = [0] * c
    cur[0] = grid[0][0] 
    for i in xrange(1, c):
        cur[i] = cur[i-1] + grid[0][i]
    for i in xrange(1, r):
        cur[0] += grid[i][0]
        for j in xrange(1, c):
            cur[j] = min(cur[j-1], cur[j]) + grid[i][j]
    return cur[-1]

# change the grid itself  
def minPathSum4(self, grid):
    if not grid:
        return 
    r, c = len(grid), len(grid[0])
    for i in xrange(1, c):
        grid[0][i] += grid[0][i-1]
    for i in xrange(1, r):
        grid[i][0] += grid[i-1][0]
    for i in xrange(1, r):
        for j in xrange(1, c):
            grid[i][j] += min(grid[i-1][j], grid[i][j-1])
    return grid[-1][-1]



def helper(self, x, y, grid, cost):
    M, N = len(grid), len(grid[0])
    if x == M or y == N:
        return float('inf')
    elif cost[x][y] != -1:
        return cost[x][y]
    else:
        right, down = self.helper(x,y+1,grid,cost), self.helper(x+1,y,grid,cost)
        cost[x][y] = min(right, down) + grid[x][y]
    return cost[x][y]

def minPathSum(self, grid):
    M, N = len(grid), len(grid[0])
    cost = [[-1]*N for _ in range(M)]
    cost[M-1][N-1] = grid[M-1][N-1]
    return self.helper(0, 0, grid, cost)


def minPathSum(self, grid):
    M, N = len(grid), len(grid[0])
    cost = [[0]*N for _ in range(M)]
    cost[0][0] = grid[0][0]
    for j in range(1,N):
        cost[0][j] = grid[0][j] + cost[0][j-1]
    for i in range(1,M):
        cost[i][0] = grid[i][0] + cost[i-1][0]
    for i in range(1,M):
        for j in range(1,N):
            cost[i][j] = min(cost[i-1][j], cost[i][j-1]) + grid[i][j]
    return cost[M-1][N-1]


def minPathSum(self, grid):
    M, N = len(grid), len(grid[0])
    cost = [float('inf')]*N
    for i in range(M):
        cost[0] = grid[i][0] + cost[0] if i > 0 else grid[i][0]
        for j in range(1,N):
            cost[j] = min(cost[j-1], cost[j]) + grid[i][j]
    return cost[-1]


def minPathSum(self, grid):
    M, N = len(grid), len(grid[0])
    for i in range(M):
        grid[i][0] = grid[i][0] + grid[i-1][0] if i > 0 else grid[i][0]
        for j in range(1,N):
            grid[i][j] = min(grid[i-1][j], grid[i][j-1]) + grid[i][j] if i > 0 else grid[i][j-1]+grid[i][j]
    return grid[-1][-1]





















































