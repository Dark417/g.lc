# 694. 不同岛屿的数量


def numDistinctIslands(self, grid: List[List[int]]) -> int:
    def dfs(x, y, path, start_x, start_y):
        for k in range(4):
            next_x, next_y = x + offset[k], y + offset[k + 1]
            if 0 <= next_x < m and 0 <= next_y < n and grid[next_x][next_y] == 1:
                grid[next_x][next_y] = 0
                path.append((next_x - start_x, next_y - start_y))
                path = dfs(next_x, next_y, path, start_x, start_y)
        return path

    shape = set()
    m, n = len(grid), len(grid[0])
    offset = [1, 0, -1, 0, 1]

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                grid[i][j] = 0
                path = dfs(i, j, [(0, 0)], i, j)
                path.sort()	# unnecessary
                shape.add(tuple(path))
    return len(shape)




def numDistinctIslands(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    islands = set()
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                stack = [(i,j)]
                self.dfs(grid, i, j, stack)
                islands.add(tuple(stack[1:]))
    return len(islands)


def dfs(self, grid, raw, col, stack):
    directions = {(1, 0), (-1, 0), (0, 1), (0, -1)}
    m, n = len(grid), len(grid[0])
    grid[raw][col] = 2
    origin = stack[0]
    stack.append((raw-origin[0], col-origin[1]))
    for dirc in directions:
        new_r, new_c = raw + dirc[0], col + dirc[1]
        if 0<=new_r<m and 0<=new_c<n:
            if grid[new_r][new_c] == 1:
                self.dfs(grid, new_r, new_c, stack)


def numDistinctIslands(self, grid: List[List[int]]) -> int:
    def dfs(grid, i, j, path):
        grid[i][j] = 2
        org = path[0]
        for x, y in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
            if 0 <= x < n and 0 <= y < m and grid[x][y] == 1:
                path.append((x - org[0], y - org[1]))
                dfs(grid, x, y, path)
    n, m = len(grid), len(grid[0])
    res = set()
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                path = [(i, j)]
                dfs(grid, i, j, path)
                path = tuple(path[1:])
                if path not in res:
                    res.add(path)
    return len(res)




def numDistinctIslands(self, grid: List[List[int]]) -> int:
    if not grid: return 0
    h, w = len(grid), len(grid[0])
    islands = []
    for i in range(h):
        for j in range(w):
            if grid[i][j] == 1:
                grid[i][j] = 2 # 标记被访问过
                stack = [(i, j)]
                island = []
                while stack:
                    x, y = stack.pop()
                    island.append((x-i, y-j)) # 记录相对于这个岛进入点的位置
                    for a, b in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        a, b = a+x, b+y
                        if 0<=a<h and 0<=b<w and grid[a][b] == 1:
                            stack.append((a, b))
                            grid[a][b] = 2
                if island not in islands:
                    islands.append(island)
    return len(islands)




def numDistinctIslands(self, grid: List[List[int]]) -> int:
    if not grid:
        return 0
    n , m = len(grid) , len(grid[0])
    flag = []
    res = []
    cnt = 0
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                ans = collections.deque()
                ans.append((i,j))
                while ans:
                    x , y = ans.popleft()
                    grid[x][y] = 0
                    for xi , yi in [(x-1,y),(x+1,y),(x,y+1),(x,y-1)]:
                        if 0 <= xi < n and 0 <= yi < m and grid[xi][yi] == 1:
                            res.append((xi-i,yi-j))
                            ans.append((xi,yi))
                            grid[xi][yi] = 0
                if res not in flag:
                    flag.append(res)
                    cnt += 1
                res = []
    return cnt







