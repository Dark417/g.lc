# 695. 岛屿的最大面积


def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
    def dfs(grid, i, j):
        if 0 <= i < n and 0 <= j < m and grid[i][j] == 1:
            self.m += 1
            grid[i][j] = 0
            dfs(grid, i - 1, j)
            dfs(grid, i + 1, j)
            dfs(grid, i, j - 1)
            dfs(grid, i, j + 1)

    mx = 0
    n, m = len(grid), len(grid[0])
    for i in range(n):
        for j in range(m):
            self.m = 0
            if grid[i][j] == 1:
                dfs(grid, i, j)
                mx = max(mx, self.m)
                self.m = 0
    return mx



def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
    mx = 0
    n, m = len(grid), len(grid[0])
    
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                ma = 0
                cur = collections.deque([(i, j)])
                while cur:
                    x, y = cur.popleft()
                    if 0 <= x < n and 0 <= y < m and grid[x][y] == 1:
                        ma += 1
                        grid[x][y] = 0
                        cur.append((x - 1, y))
                        cur.append((x + 1, y))
                        cur.append((x, y - 1))
                        cur.append((x, y + 1))
                mx = max(mx, ma)
    return mx



def maxAreaOfIsland(self, grid):
    grid = {i + j*1j: val for i, row in enumerate(grid) for j, val in enumerate(row)}
    def area(z):
        return grid.pop(z, 0) and 1 + sum(area(z + 1j**k) for k in range(4))
    return max(map(area, set(grid)))


# dfs
def dfs(self, grid, cur_i, cur_j) -> int:
    if cur_i < 0 or cur_j < 0 or cur_i == len(grid) or cur_j == len(grid[0]) or grid[cur_i][cur_j] != 1:
        return 0
    grid[cur_i][cur_j] = 0
    ans = 1
    for di, dj in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
        next_i, next_j = cur_i + di, cur_j + dj
        ans += self.dfs(grid, next_i, next_j)
    return ans

def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
    ans = 0
    for i, l in enumerate(grid):
        for j, n in enumerate(l):
            ans = max(self.dfs(grid, i, j), ans)
    return ans



# bfs + stack
def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
    ans = 0
    for i, l in enumerate(grid):
        for j, n in enumerate(l):
            cur = 0
            stack = [(i, j)]
            while stack:
                cur_i, cur_j = stack.pop()
                if cur_i < 0 or cur_j < 0 or cur_i == len(grid) or cur_j == len(grid[0]) or grid[cur_i][cur_j] != 1:
                    continue
                cur += 1
                grid[cur_i][cur_j] = 0
                for di, dj in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                    next_i, next_j = cur_i + di, cur_j + dj
                    stack.append((next_i, next_j))
            ans = max(ans, cur)
    return ans



# bfs
def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
    ans = 0
    for i, l in enumerate(grid):
        for j, n in enumerate(l):
            cur = 0
            q = collections.deque([(i, j)])
            while q:
                cur_i, cur_j = q.popleft()
                if cur_i < 0 or cur_j < 0 or cur_i == len(grid) or cur_j == len(grid[0]) or grid[cur_i][cur_j] != 1:
                    continue
                cur += 1
                grid[cur_i][cur_j] = 0
                for di, dj in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                    next_i, next_j = cur_i + di, cur_j + dj
                    q.append((next_i, next_j))
            ans = max(ans, cur)
    return ans





























