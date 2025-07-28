# 面试题 16.19. 水域大小

def pondSizes(self, land: List[List[int]]) -> List[int]:
    def dfs(x, y):
        land[x][y] = 1
        
        circum = [(x-1, y-1), (x-1, y), (x-1,y+1), (x, y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]
        for k,j in circum:
            if k>=0 and k<nr and j>=0 and j<nc and land[k][j] == 0:
                self.cnt += 1
                dfs(k,j)
        
    if not land:
        return 0
    
    nr, nc = len(land), len(land[0])
    l = []
    
    for i in range(nr):
        for j in range(nc):
            if land[i][j] == 0:
                self.cnt = 1
                dfs(i, j)
                l.append(self.cnt)
    
    return sorted(l)


def pondSizes(self, land: List[List[int]]) -> List[int]:
    res = []
    for row in range(len(land)):
        for col in range(len(land[0])):
            if land[row][col] == 0:
                tmp = collections.deque()
                tmp_count = 1
                land[row][col] = -1  # 将访问的点标记进行标记
                tmp.append([row, col])
                while len(tmp) > 0:
                    x, y = tmp.popleft()
                    for new_x, new_y in [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1],
                                         [x - 1, y - 1], [x - 1, y + 1], [x + 1, y + 1], [x + 1, y - 1]]:
                        if 0 <= new_x < len(land) and 0 <= new_y < len(land[0]) and land[new_x][new_y] == 0:
                            tmp_count += 1
                            land[new_x][new_y] = -1
                            tmp.append([new_x, new_y])
                res.append(tmp_count)
    return sorted(res)












def pondSizes(self, land: List[List[int]]) -> List[int]:
    def dfs(x, y):
        land[x][y] = 1
        
        circum = [(x-1, y-1), (x-1, y), (x-1,y+1), (x, y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]
        for k,j in circum:
            if k>=0 and k<nr and j>=0 and j<nc and land[k][j] == 0:
                dfs(k,j)
        
    if not land:
        return 0
    
    nr, nc = len(land), len(land[0])
    self.cnt = 0
    
    for i in range(nr):
        for j in range(nc):
            if land[i][j] == 0:
                dfs(i, j)
                self.cnt += 1
    
    return self.cnt

































