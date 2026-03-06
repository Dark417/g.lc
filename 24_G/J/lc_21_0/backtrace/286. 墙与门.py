# 286. 墙与门


def wallsAndGates(self, rooms: List[List[int]]) -> None:
    n, m = len(rooms), len(rooms[0])
    cur = []
    for i in range(n):
        for j in range(m):
            if  rooms[i][j] == 0:
                cur.append((i, j, 0))
    while cur:
        x, y, l = cur.pop(0)
        for i, j, l in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if 0 <= i < n and 0 <= j < m and rooms[i][j] == 2147483647:
                rooms[i][j] = l + 1
                cur.append((i, j, l + 1))


def wallsAndGates(self, rooms: List[List[int]]) -> None:
    n, m = len(rooms), len(rooms[0])
    cur = []
    for i in range(n):
        for j in range(m):
            if  rooms[i][j] == 0:
                cur.append((i, j))
    level = 0
    while cur:
        level += 1
        new = []
        for x, y in cur:
            for i, j in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if 0 <= i < n and 0 <= j < m and rooms[i][j] == 2147483647:
                    rooms[i][j] = level
                    new.append((i, j))
        cur = new






def wallsAndGates(self, rooms: List[List[int]]) -> None:
    if not rooms or not rooms[0]:
        return
    
    r, c = len(rooms), len(rooms[0])
    queue = collections.deque()
    for i in range(r):
        for j in range(c):
            if rooms[i][j] == 0:
                queue.append((i, j, 0))
    
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while queue:
        curI, curJ, step = queue.popleft()
        
        for di, dj in directions:
            nextI, nextJ = curI + di, curJ + dj
            if 0 <= nextI < r and 0 <= nextJ < c and rooms[nextI][nextJ] == 2147483647:
                queue.append((nextI, nextJ, step + 1))
                rooms[nextI][nextJ] = step + 1




def wallsAndGates(self, rooms: List[List[int]]) -> None:
    if not rooms:
        return rooms
    m, n = len(rooms), len(rooms[0])

    room_queue = deque()
    for r  in range(m):
        for c in range(n):
            if rooms[r][c] == 0:
                room_queue.append((r, c, 0))
    
    while room_queue:
        r, c, dist = room_queue.popleft()
        for dr, dc in zip((-1, 1, 0, 0), (0, 0, -1, 1)):
            newr, newc = r + dr, c + dc
            if 0 <= newr < m and 0 <= newc < n and rooms[newr][newc] == 2147483647:
                rooms[newr][newc] = dist + 1
                room_queue.append((newr, newc, dist + 1))




































