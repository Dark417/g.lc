# 2025.11.19
# if 1, keep search

# collections.deque()



# mid
200. 岛屿数量
    #dfs

	130. 被围绕的区域
    # from edge
    # union-find

    286. 墙与门

    419. 棋盘上的战舰
    #题不好


    994. 腐烂的橘子
    !!

    463. 岛屿的周长
    !!!


    694. 不同岛屿的数量


    695. 岛屿的最大面积
    !
        2658. 网格图中鱼的最大数目
        


279. 完全平方数
# def dp/dfs:
#   if x == 0: return 0  # check first



322. 零钱兑换







# mid ################################################################
200. 岛屿数量
#"0" "1"
# if 1, keep search
# dfs check 0 first / gridxy = 0 first
#	so when expand, don't need to check / set 0

def dfs(self, grid, r, c):
    grid[r][c] = 0
    nr, nc = len(grid), len(grid[0])
    for x,y in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
        if 0 <= x < nr and 0 <= y < nc and grid[x][y] == "1":
            self.dfs(grid, x, y)

def numIslands(self, grid: List[List[str]]) -> int:
    nr = len(grid)
    if nr == 0:
        return 0
    nc = len(grid[0])
    res = 0
    for r in range(nr):
        for c in range(nc):
            if grid[r][c] == "1":
                res += 1
                self.dfs(grid, r, c)
    return res
# same class, parallel
	#self.dfs
	#def dfs(self,...)


def numIslands(self, grid: List[List[str]]) -> int:
    def dfs(grid, r, c):
        grid[r][c] = 0
        nr, nc = len(grid), len(grid[0])
        for x,y in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if 0 <= x < nr and 0 <= y < nc and grid[x][y] == "1":
                dfs(grid, x, y)

    nr = len(grid)
    if nr == 0:
        return 0
    nc = len(grid[0])
    res = 0
    for r in range(nr):
        for c in range(nc):
            if grid[r][c] == "1":
                res += 1
                dfs(grid, r, c)
    return res


# if 1, keep search, append to deque
def numIslands(self, grid: List[List[str]]) -> int:
    nr = len(grid)
    if nr == 0:
        return 0
    nc = len(grid[0])

    res = 0
    for r in range(nr):
        for c in range(nc):
            if grid[r][c] == "1":
                res += 1
                grid[r][c] = "0"
                neighbors = collections.deque([(r, c)])
                while neighbors:
                    ro, co = neighbors.popleft()
                    for x, y in [(ro - 1, co), (ro + 1, co), (ro, co - 1), (ro, co + 1)]:
                        if 0 <= x < nr and 0 <= y < nc and grid[x][y] == "1":
                            neighbors.append((x, y))
                            grid[x][y] = "0"
    return res





130. 被围绕的区域

def solve(self, board: List[List[str]]) -> None:
    if not board:
        return
    
    m, n = len(board), len(board[0])

    def dfs(x, y):
        if not 0 <= x < m or not 0 <= y < n or board[x][y] != 'O':
            return
        
        board[x][y] = "A"
        dfs(x + 1, y)
        dfs(x - 1, y)
        dfs(x, y + 1)
        dfs(x, y - 1)
    
    for i in range(m):
        dfs(i, 0)
        dfs(i, n - 1)
    
    for i in range(n - 1):
        dfs(0, i)
        dfs(m - 1, i)
    
    for i in range(m):
        for j in range(n):
            if board[i][j] == "A":
                board[i][j] = "O"
            elif board[i][j] == "O":
                board[i][j] = "X"




def solve(self, board: List[List[str]]) -> None:
    if not board: return
    
    m, n = len(board), len(board[0])
    queue = deque()
    
    # 1. Initialize Queue with all boundary 'O's
    for i in range(m):
        if board[i][0] == "O":
            queue.append((i, 0))
            board[i][0] = "A" # Mark visited/safe immediately
        if board[i][n - 1] == "O":
            queue.append((i, n - 1))
            board[i][n - 1] = "A"

    for j in range(n):
        # Check 0 and m-1, avoiding duplicates if corners already added
        # (Duplicate check isn't strictly necessary due to "A" check, but good for clarity)
        if board[0][j] == "O":
            queue.append((0, j))
            board[0][j] = "A"
        if board[m - 1][j] == "O":
            queue.append((m - 1, j))
            board[m - 1][j] = "A"
    
    # 2. Process Queue (The Wave)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    while queue:
        r, c = queue.popleft()
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            # If valid range AND is an 'O' (unvisited)
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == "O":
                board[nr][nc] = "A" # Mark safe
                queue.append((nr, nc)) # Add to queue to continue wave
    
    # 3. Final Sweep
    for i in range(m):
        for j in range(n):
            if board[i][j] == "O":
                board[i][j] = "X" # These were never reached from the edge
            elif board[i][j] == "A":
                board[i][j] = "O" # These are the survivors


###union-find
from typing import List
class UnionFind:
    def __init__(self, size):
        # Parent array: Initially each node is its own parent
        self.parent = list(range(size))
        # Rank: To keep tree height low during union
        self.rank = [1] * size

    def find(self, p):
        # Path Compression: Point directly to the root for O(1) avg access
        if self.parent[p] != p:
            self.parent[p] = self.find(self.parent[p])
        return self.parent[p]

    def union(self, p, q):
        rootP = self.find(p)
        rootQ = self.find(q)
        
        if rootP != rootQ:
            # Union by Rank: Attach smaller tree to larger tree
            if self.rank[rootP] > self.rank[rootQ]:
                self.parent[rootQ] = rootP
            elif self.rank[rootP] < self.rank[rootQ]:
                self.parent[rootP] = rootQ
            else:
                self.parent[rootQ] = rootP
                self.rank[rootP] += 1
            return True
        return False

    def is_connected(self, p, q):
        return self.find(p) == self.find(q)


class Solution:
    def solve(self, board: List[List[str]]) -> None:
        """
        DSU Approach:
        1. Map 2D coordinates (r, c) to 1D index: index = r * n + c.
        2. Create a 'Dummy Node' at index (m * n) representing the "Border".
        3. Iterate through board:
           - If 'O' is on border: Union(node, DummyNode).
           - If 'O' has 'O' neighbor: Union(node, neighbor).
        4. Final pass: If find(node) != find(DummyNode), flip it.
        """
        if not board or not board[0]:
            return

        m, n = len(board), len(board[0])
        # The dummy node is the last index (m * n)
        dummy_node = m * n
        dsu = UnionFind(m * n + 1)

        for i in range(m):
            for j in range(n):
                if board[i][j] == "O":
                    current_idx = i * n + j
                    
                    # 1. Check if connected to Border (Union with Dummy)
                    if i == 0 or i == m - 1 or j == 0 or j == n - 1:
                        dsu.union(current_idx, dummy_node)
                    
                    # 2. Check connections to neighbors (Only need Down and Right to cover all)
                    # We check 'current' vs 'neighbor'. 
                    # If both are 'O', we unite them.
                    
                    # Check Right
                    if j + 1 < n and board[i][j+1] == "O":
                        right_idx = i * n + (j + 1)
                        dsu.union(current_idx, right_idx)
                    
                    # Check Down
                    if i + 1 < m and board[i+1][j] == "O":
                        down_idx = (i + 1) * n + j
                        dsu.union(current_idx, down_idx)

        # 3. Final Sweep
        for i in range(m):
            for j in range(n):
                if board[i][j] == "O":
                    current_idx = i * n + j
                    # If NOT connected to the dummy border node, it is trapped.
                    if not dsu.is_connected(current_idx, dummy_node):
                        board[i][j] = "X"





286. 墙与门
#bfs
# if == EMPTY: visted
# two gate visit same cell, the val is the same
class Solution:
    EMPTY = 2147483647
    GATE  = 0
    DIRS  = [(1,0), (-1,0), (0,1), (0,-1)]

    def wallsAndGates(self, rooms: List[List[int]]) -> None:
        m, n = len(rooms), len(rooms[0])
        q = deque()

        for i in range(m):
            for j in range(n):
                if rooms[i][j] == self.GATE:
                    q.append((i, j))
        while q:
            r, c = q.popleft()
            for dr, dc in self.DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and rooms[nr][nc] == self.EMPTY:
                    rooms[nr][nc] = rooms[r][c] + 1
                    q.append((nr, nc))

#dfs
class Solution:
    EMPTY = 2147483647
    GATE  = 0
    WALL  = -1
    DIRS  = [(1,0), (-1,0), (0,1), (0,-1)]

    def wallsAndGates(self, rooms: List[List[int]]) -> None:
        m, n = len(rooms), len(rooms[0])
        q = deque()

        for i in range(m):
            for j in range(n):
                if rooms[i][j] == self.GATE:
                    self._dfs_flood_fill(rooms, i, j, 0)
        
    def _dfs_flood_fill(self, rooms: List[List[int]], r: int, c: int, distance: int) -> None:
        m, n = len(rooms), len(rooms[0])
        if not (0 <= r < m and 0 <= c < n):
            return

        if rooms[r][c] == self.WALL:
            return

        if rooms[r][c] < distance:
            return

        rooms[r][c] = distance
        
        for dr, dc in self.DIRS:
            nr, nc = r + dr, c + dc
            self._dfs_flood_fill(rooms, nr, nc, distance + 1)

#brute
class Solution:
    EMPTY = 2147483647
    GATE  = 0
    WALL  = -1
    DIRECTIONS = [(1,0), (-1,0), (0,1), (0,-1)]

    def wallsAndGates(self, rooms: List[List[int]]) -> None:
        if not rooms:
            return
        m, n = len(rooms), len(rooms[0])
        for row in range(m):
            for col in range(n):
                if rooms[row][col] == self.EMPTY:
                    rooms[row][col] = self.distanceToNearestGate(rooms, row, col)

    def distanceToNearestGate(self, rooms: List[List[int]], sr: int, sc: int) -> int:
        m, n = len(rooms), len(rooms[0])
        dist = [[0] * n for _ in range(m)]
        q = collections.deque([(sr, sc)])

        while q:
            row, col = q.popleft()
            for dr, dc in self.DIRECTIONS:
                r, c = row + dr, col + dc
                #We stop visiting a node because the first time we reach it, we guarantee we have found the shortest possible path to that node.
                if r < 0 or c < 0 or r >= m or c >= n or rooms[r][c] == self.WALL or dist[r][c]:
                    continue
                dist[r][c] = dist[row][col] + 1
                if rooms[r][c] == self.GATE:
                    return dist[r][c]
                q.append((r, c))

        return self.EMPTY




419. 棋盘上的战舰

def countBattleships(self, board: List[List[str]]) -> int:
    ans = 0
    m, n = len(board), len(board[0])
    for i, row in enumerate(board):
        for j, ch in enumerate(row):
            if ch == 'X':
                row[j] = '.'
                for k in range(j + 1, n):
                    if row[k] != 'X':
                        break
                    row[k] = '.'
                for k in range(i + 1, m):
                    if board[k][j] != 'X':
                        break
                    board[k][j] = '.'
                ans += 1
    return ans


#箭头左上无
def countBattleships(self, board: List[List[str]]) -> int:
    ans = 0
    for i, row in enumerate(board):
        for j, c in enumerate(row):
            if c == 'X' and (j == 0 or row[j - 1] != 'X') and \
                            (i == 0 or board[i - 1][j] != 'X'):
                ans += 1
    return ans



994. 腐烂的橘子
def orangesRotting(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    fresh = 0
    q = []
    for i, row in enumerate(grid):
        for j, x in enumerate(row):
            if x == 1:
                fresh += 1  # 统计新鲜橘子个数
            elif x == 2:
                q.append((i, j))  # 一开始就腐烂的橘子

    ans = 0
    while q and fresh:
        ans += 1  # 经过一分钟
        tmp = q
        q = []
        for x, y in tmp:  # 已经腐烂的橘子
            for i, j in (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1):  # 四方向
                if 0 <= i < m and 0 <= j < n and grid[i][j] == 1:  # 新鲜橘子
                    fresh -= 1
                    grid[i][j] = 2  # 变成腐烂橘子
                    q.append((i, j))

    return -1 if fresh else ans


def orangesRotting(self, grid: List[List[int]]) -> int:
    M = len(grid)
    N = len(grid[0])
    queue = []
    
    count = 0 # count 表示新鲜橘子的数量
    for r in range(M):
        for c in range(N):
            if grid[r][c] == 1:
                count += 1
            elif grid[r][c] == 2:
                queue.append((r, c))
                
    round = 0 # round 表示腐烂的轮数，或者分钟数
    while count > 0 and len(queue) > 0:
        round += 1 
        n = len(queue)
        for i in range(n):
            r, c = queue.pop(0)
            if r-1 >= 0 and grid[r-1][c] == 1:
                grid[r-1][c] = 2
                count -= 1
                queue.append((r-1, c))
            if r+1 < M and grid[r+1][c] == 1:
                grid[r+1][c] = 2
                count -= 1
                queue.append((r+1, c))
            if c-1 >= 0 and grid[r][c-1] == 1:
                grid[r][c-1] = 2
                count -= 1
                queue.append((r, c-1))
            if c+1 < N and grid[r][c+1] == 1:
                grid[r][c+1] = 2
                count -= 1
                queue.append((r, c+1))
    
    if count > 0:
        return -1
    else:
        return round



463. 岛屿的周长
def islandPerimeter(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    ans = 0
    for i, row in enumerate(grid):
        for j, x in enumerate(row):
            if x == 0:
                continue
            if i == 0 or grid[i - 1][j] == 0:  # 上：出界或者是水
                ans += 1
            if i == m - 1 or grid[i + 1][j] == 0:  # 下：出界或者是水
                ans += 1
            if j == 0 or row[j - 1] == 0:  # 左：出界或者是水
                ans += 1
            if j == n - 1 or row[j + 1] == 0:  # 右：出界或者是水
                ans += 1
    return ans

def islandPerimeter(self, grid: List[List[int]]) -> int:
    r, c = len(grid), len(grid[0])
    sm = sum(i for r in grid for i in r)
    sm *= 4
    for i in range(r):
        for j in range(c):
            if j != c-1 and grid[i][j] == grid[i][j+1] == 1:
                sm -= 2
            if i != r-1 and grid[i][j] == grid[i+1][j] == 1:
                sm -= 2
    return sm



694. 不同岛屿的数量





695. 岛屿的最大面积
def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])

    def dfs(i: int, j: int) -> int:
        area = 1  # (i,j) 这个格子
        grid[i][j] = 0  # 标记 (i,j) 访问过
        for x, y in (i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j):  # 左右上下
            if 0 <= x < m and 0 <= y < n and grid[x][y]:
                # 把统计岛屿面积的任务交给其他人去处理，自己只需累加其他人统计出来的岛屿面积
                area += dfs(x, y)
        return area

    # ans = 0
    # for i, row in enumerate(grid):
    #     for j, x in enumerate(row):
    #         if x:  # 是陆地，且之前没有访问过
    #             ans = max(ans, dfs(i, j))
    # return ans
    return max((dfs(i, j) for i in range(m) for j in range(n) if grid[i][j]), default=0)



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


def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    max_area = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                queue = collections.deque([(r, c)])
                current_area = 0
                while queue:
                    row, col = queue.popleft()
                    if grid[row][col] == 1:
                        grid[row][col] = 0
                        current_area += 1
                        for dr, dc in (0, 1), (0, -1), (1, 0), (-1, 0):
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < rows and 0 <= nc < cols:
                                if grid[nr][nc] == 1:
                                    queue.append((nr, nc))
                max_area = max(max_area, current_area)

    return max_area



2658. 网格图中鱼的最大数目
def findMaxFish(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    def dfs(i, j):
        if 0 <= i < m and 0 <= j < n and grid[i][j] > 0:
            s = grid[i][j]
            grid[i][j] = 0
            for x, y in (i-1,j),(i+1,j),(i,j-1),(i,j+1):
                s += dfs(x, y)
            return s
        else:
            return 0
    return max(max(dfs(i, j) for j in range(n)) for i in range(m))

def findMaxFish(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    def dfs(i: int, j: int) -> int:
        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] == 0:
            return 0
        s = grid[i][j]
        grid[i][j] = 0  # 标记成访问过
        for x, y in (i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1):
            s += dfs(x, y)  # 四方向移动
        return s
    return max(max(dfs(i, j) for j in range(n)) for i in range(m))


def findMaxFish(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    max_fish = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] > 0:
                queue = collections.deque([(r, c)])
                total_fish = 0
                while queue:
                    i, j = queue.popleft()
                    if grid[i][j] > 0:
                        total_fish += grid[i][j]
                        grid[i][j] = 0
                        for nr, nc in (i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1):
                            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] > 0:
                                queue.append((nr, nc))
                max_fish = max(max_fish, total_fish)
    return max_fish
        
def findMaxFish(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    max_fish = 0

    def bfs(start_r: int, start_c: int) -> int:
        queue = collections.deque([(start_r, start_c)])
        total_fish = 0
        while queue:
            r, c = queue.popleft()
            if grid[r][c] > 0:
                total_fish += grid[r][c]
                grid[r][c] = 0
                for dr, dc in (0, 1), (0, -1), (1, 0), (-1, 0):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] > 0:
                        queue.append((nr, nc))         
        return total_fish

    for i in range(m):
        for j in range(n):
            if grid[i][j] > 0:
                max_fish = max(max_fish, bfs(i, j))
    return max_fish




279. 完全平方数


# call stack as memo storage

# init* i == 0: return 0
# f[0] = 0
# get min, init with inf
# inf


def numSquares_dp(self, n: int) -> int:
    f = [float('inf')] * (n + 1)
    f[0] = 0

    for i in range(1, n + 1):
        minn = float('inf')
        j = 1
        while j * j <= i:
            minn = min(minn, f[i - j * j])
            j += 1

        f[i] = minn + 1
    
    return f[n]


N = 10000
f = [[0] * (N + 1) for _ in range(isqrt(N) + 1)]
f[0] = [0] + [inf] * N
for i in range(1, len(f)):
    for j in range(N + 1):
        if j < i * i:
            f[i][j] = f[i - 1][j]  # 只能不选
        else:
            f[i][j] = min(f[i - 1][j], f[i][j - i * i] + 1)  # 不选 vs 选

class Solution:
    def numSquares(self, n: int) -> int:
        return f[isqrt(n)][n]  # 也可以写 f[-1][n]


# instead of iter from i, 
#   iter from i*i!
N = 10000
f = [0] + [inf] * N
for i in range(1, isqrt(N) + 1):
    for j in range(i * i, N + 1):
        f[j] = min(f[j], f[j - i * i] + 1)  # 不选 vs 选

class Solution:
    def numSquares(self, n: int) -> int:
        return f[n]



@cache  # 缓存装饰器，避免重复计算 dfs 的结果（记忆化）
def dfs(i: int, j: int) -> int:
    if i == 0:
        return inf if j else 0
    if j < i * i:
        return dfs(i - 1, j)  # 只能不选
    return min(dfs(i - 1, j), dfs(i, j - i * i) + 1)  # 不选 vs 选

class Solution:
    def numSquares(self, n: int) -> int:
        return dfs(isqrt(n), n)



def numSquares_memo_dp(self, n: int) -> int:
    squares = [i * i for i in range(1, int(math.sqrt(n)) + 1)]

    @functools.lru_cache(n)
    def dp(rem: int) -> int:
        if rem == 0:
            return 0
        mini = float('inf')
        for square in squares:
            next_rem = rem - square
            if next_rem < 0:
                break
            res = dp(next_rem)
            if res != float('inf'):
                mini = min(mini, res + 1)
        return mini

    result = dp(n)
    return int(result)


def numSquares_bfs(self, n: int) -> int:
    if n <= 0: return 0
    squares = [i * i for i in range(1, int(math.sqrt(n)) + 1)]
    queue = deque([(n, 0)])
    visited = {n} # Use a set to prevent revisiting states and infinite loops
    
    while queue:
        current_n, steps = queue.popleft()
        
        if current_n == 0:
            return steps
        
        for square in squares:
            next_n = current_n - square
            
            if next_n < 0:
                break
            
            if next_n not in visited:
                visited.add(next_n)
                queue.append((next_n, steps + 1))
    
    # Should not be reached based on Lagrange's theorem (max answer is 4)
    return n



# --- 4. Depth-First Search (DFS) + Pruning Method ---
# Time Complexity: Difficult to determine precisely, faster than naive DFS but slower than BFS
# Space Complexity: O(n) (for the recursion stack)
def numSquares_dfs(self, n: int) -> int:
    squares = [i * i for i in range(1, int(math.sqrt(n)) + 1)][::-1] 

    for k in range(1, 5): 
        if self._dfs_check(n, k, squares):
            return k
    # Fallback, though guaranteed to be found by k=4
    return 4 


def _dfs_check(self, target: int, k: int, squares: List[int]) -> bool:
    """
    Checks if the target can be summed by k perfect squares.
    :param target: The remaining target number
    :param k: The number of perfect squares allowed
    :param squares: List of perfect squares (sorted descending)
    """
    if k == 1:
        # Base case: Check if the target itself is a perfect square
        return int(math.sqrt(target))**2 == target

    # If k > 1, try subtracting one square (s)
    for s in squares:
        if s > target:
            continue
        
        # Recursive call: Check if target - s can be formed by k-1 squares
        if self._dfs_check(target - s, k - 1, squares):
            return True
    
    return False


# --- 3. Mathematical Method (Legendre's Three-Square Theorem) ---
# Time Complexity: O(sqrt(n)) - The fastest approach
# Space Complexity: O(1)
def numSquares_math(self, n: int) -> int:
    """
    Mathematical solution based on number theory: Lagrange's Four-Square Theorem 
    and Legendre's Three-Square Theorem.
    
    1. Any positive integer can be represented as the sum of at most four squares.
    2. Answer is 1 if n is a perfect square.
    3. Answer is 4 if n is of the form 4^k * (8m + 7).
    4. Answer is 2 if n can be represented as a^2 + b^2.
    5. Otherwise, the answer must be 3.
    """
    
    # Step 1: Check for answer 1 (n itself is a perfect square)
    if int(math.sqrt(n))**2 == n:
        return 1

    # Helper function: Checks if n satisfies the form n = 4^k * (8m + 7)
    def is_sum_of_four(num):
        # Continuously divide n by 4 until it's no longer divisible
        while num % 4 == 0:
            num //= 4
        # Check if the remaining number satisfies the (8m + 7) form
        return num % 8 == 7

    # Step 2: Check for answer 4 (based on Legendre's theorem)
    if is_sum_of_four(n):
        return 4

    # Step 3: Check for answer 2 (n is a sum of two perfect squares)
    # Check if there exist two numbers a, b such that n = a^2 + b^2
    i = 1
    while i * i <= n:
        j_square = n - i * i
        # Check if n - i*i is also a perfect square
        if int(math.sqrt(j_square))**2 == j_square:
            return 2
        i += 1

    # Step 4: The answer must be 3 (if it's not 1, 2, or 4, it must be 3)
    return 3



        
322. 零钱兑换
dp(i, c)
Failure: i < 0 AND c > 0. You ran out of available items before reaching the target.    
Success: i < 0 AND c == 0. You ran out of items exactly at the target.

def coinChange(self, coins: List[int], amount: int) -> int:
    @cache  # 缓存装饰器，避免重复计算 dfs 的结果（记忆化）
    def dfs(i: int, c: int) -> int:
        if i < 0:
            return 0 if c == 0 else inf
        if c < coins[i]:  # 只能不选
            return dfs(i - 1, c)
        # 不选 vs 继续选
        return min(dfs(i - 1, c), dfs(i, c - coins[i]) + 1)

    ans = dfs(len(coins) - 1, amount)
    return ans if ans < inf else -1



def coinChange(self, coins: List[int], amount: int) -> int:
    @functools.lru_cache(amount)
    def dp(rem):
        if rem < 0: return -1
        if rem == 0: return 0
        mini = int(1e9)
        for coin in self.coins:
            res = dp(rem - coin)
            if res >= 0 and res < mini:
                mini = res + 1
        return mini if mini < int(1e9) else -1
    self.coins = coins
    return dp(amount) if amount >= 1 else 0



def coinChange(self, coins: List[int], amount: int) -> int:
    if amount == 0:
        return 0
    coins.sort(reverse=True) 
    @functools.cache
    def dp(rem: int) -> float:
        if rem < 0:
            return math.inf
        if rem == 0:
            return 0.0
                    mini = math.inf
        for coin in coins:
            result = dp(rem - coin)

            if result != math.inf:
                mini = min(mini, result + 1)
        return mini
    min_coins = dp(amount)
    return int(min_coins) if min_coins != math.inf else -1



def coinChange(self, coins: List[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1



def coinChange_dp_bu(self, coins: List[int], amount: int) -> int:
    if amount == 0:
        return 0
        
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if i - coin >= 0:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return int(dp[amount]) if dp[amount] != float('inf') else -1


def coinChange_dp_td(self, coins: List[int], amount: int) -> int:
    if amount == 0:
        return 0
    coins.sort(reverse=True)
    @functools.lru_cache(amount)
    def dp(rem: int) -> int:
        if rem == 0:
            return 0
        if rem < 0:
            return -1 # Impossible state
        mini = float('inf')
        for coin in coins:
            res = dp(rem - coin)
            if res >= 0:
                mini = min(mini, res + 1)
        return mini if mini != float('inf') else -1
    
    return dp(amount)

#!!! good
def coinChange_bfs(self, coins: List[int], amount: int) -> int:
    if amount == 0:
        return 0
    coins.sort(reverse=True)
    queue = deque([(amount, 0)])
    visited = {amount} 
    
    while queue:
        current_rem, steps = queue.popleft()
        for coin in coins:
            next_rem = current_rem - coin
            if next_rem == 0:
                return steps + 1
            if next_rem < 0:
                break
            if next_rem not in visited:
                visited.add(next_rem)
                queue.append((next_rem, steps + 1))
    return -1


#no
def coinChange_dfs(self, coins: List[int], amount: int) -> int:
    if amount == 0:
        return 0
    coins.sort(reverse=True)
    self.min_coins = float('inf')

    def dfs(idx: int, rem: int, count: int) -> None:
        if rem == 0:
            self.min_coins = min(self.min_coins, count)
            return
        if count + 1 >= self.min_coins:
            return
        coin = coins[idx]
        max_uses = rem // coin
        for k in range(max_uses, -1, -1):
            new_rem = rem - k * coin
            new_count = count + k
            if new_count >= self.min_coins:
                continue 

            if idx < len(coins) - 1:
                dfs(idx + 1, new_rem, new_count)
            elif new_rem == 0:

                self.min_coins = min(self.min_coins, new_count)

    dfs(0, amount, 0)
    
    return int(self.min_coins) if self.min_coins != float('inf') else -1

































































































