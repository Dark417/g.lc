# 994. 腐烂的橘子

# return t, updated in iteration
def orangesRotting(self, grid: List[List[int]]) -> int:
    n, m, t = len(grid), len(grid[0]), 0
    cur = [(i, j, 0) for i in range(n) for j in range(m) if grid[i][j] == 2]
    while cur:
        i, j, t = cur.pop(0)
        for x, y in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
            if 0 <= x < n and 0 <= y < m and grid[x][y] == 1:
                grid[x][y] = 2
                cur.append((x, y, t + 1))
    return -1 if any(grid[i][j] == 1 for i in range(n) for j in range(m)) else t






















