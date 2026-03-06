# 130. 被围绕的区域



# uni-find
def solve(self, board: List[List[str]]) -> None:
    f = {}
    def find(x):
        f.setdefault(x, x)
        if f[x] != x:
            f[x] = find(f[x])
        return f[x]
    def union(x, y):
        f[find(y)] = find(x)

    if not board or not board[0]:
        return
    row = len(board)
    col = len(board[0])
    dummy = row * col
    for i in range(row):
        for j in range(col):
            if board[i][j] == "O":
                if i == 0 or i == row - 1 or j == 0 or j == col - 1:
                    union(i * col + j, dummy)
                else:
                    for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if board[i + x][j + y] == "O":
                            union(i * col + j, (i + x) * col + (j + y))
    for i in range(row):
        for j in range(col):
            if find(dummy) == find(i * col + j):
                board[i][j] = "O"
            else:
                board[i][j] = "X"




# dfs
# 可以在外面检查，或者里面
def solve(self, board: List[List[str]]) -> None:
    def red(board, i, j):
        if 0 <= i < n and 0 <= j < m and board[i][j] == "O":
            board[i][j] = "R"
            red(board, i - 1, j)
            red(board, i + 1, j)
            red(board, i, j - 1)
            red(board, i, j + 1)
    
    n, m = len(board), len(board[0])
    for i in range(n):
        red(board, i, 0)
        red(board, i, m - 1)
        
    for j in range(m):
        red(board, 0, j)
        red(board, n - 1, j)
    
    
    for i in range(n):
        for j in range(m):
            if board[i][j] == "O":
                board[i][j] = "X"
                
    for i in range(n):
        for j in range(m):
            if board[i][j] == "R":
                board[i][j] = "O"


# bfs













def solve(self, board: List[List[str]]) -> None:
    if not board:
        return
    
    n, m = len(board), len(board[0])

    def dfs(x, y):
        if not 0 <= x < n or not 0 <= y < m or board[x][y] != 'O':
            return
        
        board[x][y] = "A"
        dfs(x + 1, y)
        dfs(x - 1, y)
        dfs(x, y + 1)
        dfs(x, y - 1)
    
    for i in range(n):
        dfs(i, 0)
        dfs(i, m - 1)
    
    for i in range(m - 1):
        dfs(0, i)
        dfs(n - 1, i)
    
    for i in range(n):
        for j in range(m):
            if board[i][j] == "A":
                board[i][j] = "O"
            elif board[i][j] == "O":
                board[i][j] = "X"



def solve(self, board: List[List[str]]) -> None:
    if not board:
        return
    
    n, m = len(board), len(board[0])
    que = collections.deque()
    for i in range(n):
        if board[i][0] == "O":
            que.append((i, 0))
        if board[i][m - 1] == "O":
            que.append((i, m - 1))
    for i in range(m - 1):
        if board[0][i] == "O":
            que.append((0, i))
        if board[n - 1][i] == "O":
            que.append((n - 1, i))
    
    while que:
        x, y = que.popleft()
        board[x][y] = "A"
        for mx, my in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if 0 <= mx < n and 0 <= my < m and board[mx][my] == "O":
                que.append((mx, my))
    
    for i in range(n):
        for j in range(m):
            if board[i][j] == "A":
                board[i][j] = "O"
            elif board[i][j] == "O":
                board[i][j] = "X"


def solve(self, board: List[List[str]]) -> None:
    if not board or not board[0]:
        return
    row = len(board)
    col = len(board[0])

    def bfs(i, j):
        from collections import deque
        queue = deque()
        queue.appendleft((i, j))
        while queue:
            i, j = queue.pop()
            if 0 <= i < row and 0 <= j < col and board[i][j] == "O":
                board[i][j] = "B"
                for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    queue.appendleft((i + x, j + y))
    for j in range(col):
        if board[0][j] == "O":
            bfs(0, j)
        if board[row - 1][j] == "O":
            bfs(row - 1, j)

    for i in range(row):

        if board[i][0] == "O":
            bfs(i, 0)
        if board[i][col - 1] == "O":
            bfs(i, col - 1)

    for i in range(row):
        for j in range(col):
            if board[i][j] == "O":
                board[i][j] = "X"
            if board[i][j] == "B":
                board[i][j] = "O"



