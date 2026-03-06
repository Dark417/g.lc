# 1034. 边框着色


def colorBorder(self, grid: List[List[int]], r0: int, c0: int, color: int) -> List[List[int]]:   
    def dfs(i, j):
        for x, y in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
            if 0 <= x < n and 0 <= y < m:
                if (x, y) not in self.v:
                    if grid[x][y] == old:
                        self.v.add((x, y))
                        dfs(x, y)
                    else:
                        grid[i][j] = color
            else:
                grid[i][j] = color
            
    n, m = len(grid), len(grid[0])
    self.v = set()
    old = grid[r0][c0]
    dfs(r0, c0)
    return grid


def colorBorder(self, grid: List[List[int]], r0: int, c0: int, color: int) -> List[List[int]]:
    if not grid:
        return []
    pos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
    m, n = len(grid), len(grid[0])
    visited = set()
    visited.add((r0,c0))
    target=grid[r0][c0]
    def dfs(x, y):
        for i,j in pos:
            a=x+i
            b=y+j
			if 0 <= a < m and 0 <= b < n:
                if (a,b) not in visited:
                    if grid[a][b] == target:
                        visited.add((a,b))
                        dfs(a,b)
                    else:
                        grid[x][y] = color
            else:
                grid[x][y] = color

    dfs(r0, c0) 
    return grid


def colorBorder(self, grid: List[List[int]], r0: int, c0: int, color: int) -> List[List[int]]:
        if not grid:
            return []
        pos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        m, n = len(grid), len(grid[0])
        queue = collections.deque()
        queue.append((r0,c0))
        visited = set()
        visited.add((r0,c0))
        target=grid[r0][c0]
        while queue:
            x,y=queue.popleft()
            for i,j in pos:
                a=x+i
                b=y+j

                if 0 <= a < m and 0 <= b < n:
                    if (a,b) not in visited:
                        if grid[a][b] == target:
                            visited.add((a,b))
                            queue.append((a,b))
                        else:
                            grid[x][y] = color
                else:
                    grid[x][y] = color
        return grid


























