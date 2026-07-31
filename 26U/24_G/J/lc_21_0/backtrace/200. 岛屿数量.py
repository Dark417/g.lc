# 200. 岛屿数量

# union-find
class UnionFind:
    def __init__(self, grid):
        m, n = len(grid), len(grid[0])
        self.count = 0
        self.parent = [-1] * (m * n)
        self.rank = [0] * (m * n)
        for i in range(m):
            for j in range(n):
                if grid[i][j] == "1":
                    self.parent[i * n + j] = i * n + j
                    self.count += 1
    
    def find(self, i):
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    
    def union(self, x, y):
        rootx = self.find(x)
        rooty = self.find(y)
        if rootx != rooty:
            if self.rank[rootx] < self.rank[rooty]:
                rootx, rooty = rooty, rootx
            self.parent[rooty] = rootx
            if self.rank[rootx] == self.rank[rooty]:
                self.rank[rootx] += 1
            self.count -= 1
    
    def getCount(self):
        return self.count

class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        nr = len(grid)
        if nr == 0:
            return 0
        nc = len(grid[0])

        uf = UnionFind(grid)
        num_islands = 0
        for r in range(nr):
            for c in range(nc):
                if grid[r][c] == "1":
                    grid[r][c] = "0"
                    for x, y in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
                        if 0 <= x < nr and 0 <= y < nc and grid[x][y] == "1":
                            uf.union(r * nc + c, x * nc + y)
        
        return uf.getCount()



# Stefan
def numIslands(self, grid):
    def sink(i, j):
        if 0 <= i < len(grid) and 0 <= j < len(grid[i]) and grid[i][j] == '1':
            grid[i][j] = '0'
            map(sink, (i+1, i-1, i, i), (j, j, j+1, j-1))
            return 1
        return 0
    return sum(sink(i, j) for i in range(len(grid)) for j in range(len(grid[i])))


# dfs
def numIslands(self, grid: List[List[str]]) -> int:
    def dfs(grid, i, j, f):
        if 0 <= i < n and 0 <= j < m and grid[i][j] == "1":               
            if f == 1:
                self.res += 1
                f = 0
            grid[i][j] = "0"
            dfs(grid, i - 1, j, f)
            dfs(grid, i + 1, j, f)
            dfs(grid, i, j - 1, f)
            dfs(grid, i, j + 1, f)

    def dfs(grid, i, j, f):
            if i < 0 or i >= n or j < 0 or j >= m or grid[i][j] == "0":
                return
            if f == 1:
                self.res += 1
                f = 0
            grid[i][j] = "0"
            dfs(grid, i - 1, j, f)
            dfs(grid, i + 1, j, f)
            dfs(grid, i, j - 1, f)
            dfs(grid, i, j + 1, f)

    self.res = 0
    n, m = len(grid), len(grid[0])
    for i in range(n):
        for j in range(m):
            f = 1
            dfs(grid, i, j, f)
    return self.res



def numIslands(self, grid: List[List[str]]) -> int:
    def dfs(grid, i, j):
        if 0 <= i < n and 0 <= j < m and grid[i][j] == "1":               
            grid[i][j] = "0"
            dfs(grid, i - 1, j)
            dfs(grid, i + 1, j)
            dfs(grid, i, j - 1)
            dfs(grid, i, j + 1)

    self.res = 0
    n, m = len(grid), len(grid[0])
    for i in range(n):
        for j in range(m):
            if grid[i][j] == "1":
                self.res += 1
                dfs(grid, i, j)
    return self.res



# bfs
def numIslands(self, grid: List[List[str]]) -> int:
    res = 0
    n, m = len(grid), len(grid[0])
    for i in range(n):
        for j in range(m):
            if grid[i][j] == "1":
                res += 1
                grid[i][j] == "0"
                cur = collections.deque([(i, j)])
                while cur:
                    x, y = cur.popleft()
                    if 0 <= x < n and 0 <= y < m and grid[x][y] == "1":               
                        grid[x][y] = "0"
                        cur.append((x - 1, y))
                        cur.append((x + 1, y))
                        cur.append((x, y - 1))
                        cur.append((x, y + 1))
    return res



def dfs(self, grid, r, c):
    grid[r][c] = 0
    nr, nc = len(grid), len(grid[0])
    for x, y in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
        if 0 <= x < nr and 0 <= y < nc and grid[x][y] == "1":
            self.dfs(grid, x, y)

def numIslands(self, grid: List[List[str]]) -> int:
    nr = len(grid)
    if nr == 0:
        return 0
    nc = len(grid[0])

    num_islands = 0
    for r in range(nr):
        for c in range(nc):
            if grid[r][c] == "1":
                num_islands += 1
                self.dfs(grid, r, c)
    
    return num_islands




def numIslands(self, grid: List[List[str]]) -> int:
    nr = len(grid)
    if nr == 0:
        return 0
    nc = len(grid[0])

    num_islands = 0
    for r in range(nr):
        for c in range(nc):
            if grid[r][c] == "1":
                num_islands += 1
                grid[r][c] = "0"
                neighbors = collections.deque([(r, c)])
                while neighbors:
                    row, col = neighbors.popleft()
                    for x, y in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]:
                        if 0 <= x < nr and 0 <= y < nc and grid[x][y] == "1":
                            neighbors.append((x, y))
                            grid[x][y] = "0"
    
    return num_islands













