# 304. 二维区域和检索 - 矩阵不可变

def __init__(self, matrix: List[List[int]]):
    m, n = len(matrix), (len(matrix[0]) if matrix else 0)
    self.sums = [[0] * (n + 1) for _ in range(m)]
    _sums = self.sums

    for i in range(m):
        for j in range(n):
            _sums[i][j + 1] = _sums[i][j] + matrix[i][j]

def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
    _sums = self.sums

    total = sum(_sums[i][col2 + 1] - _sums[i][col1] for i in range(row1, row2 + 1))
    return total



def __init__(self, matrix: List[List[int]]):
    m, n = len(matrix), (len(matrix[0]) if matrix else 0)
    self.sums = [[0] * (n + 1) for _ in range(m + 1)]
    _sums = self.sums

    for i in range(m):
        for j in range(n):
            _sums[i + 1][j + 1] = _sums[i][j + 1] + _sums[i + 1][j] - _sums[i][j] + matrix[i][j]

def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
    _sums = self.sums

    return _sums[row2 + 1][col2 + 1] - _sums[row1][col2 + 1] - _sums[row2 + 1][col1] + _sums[row1][col1]



def __init__(self, matrix: List[List[int]]):
    if not matrix or not matrix[0]:
        M, N = 0, 0
    else:
        M, N = len(matrix), len(matrix[0])
    self.preSum = [[0] * (N + 1) for _ in range(M + 1)]
    for i in range(M):
        for j in range(N):
            self.preSum[i + 1][j + 1] = self.preSum[i][j + 1] + self.preSum[i + 1][j]  - self.preSum[i][j] + matrix[i][j]


def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
    return self.preSum[row2 + 1][col2 + 1] - self.preSum[row2 + 1][col1] - self.preSum[row1][col2 + 1] + self.preSum[row1][col1]





# 1314. 矩阵区域和

def matrixBlockSum(self, mat: List[List[int]], K: int) -> List[List[int]]:
    m, n = len(mat), len(mat[0])
    P = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            P[i][j] = P[i - 1][j] + P[i][j - 1] - P[i - 1][j - 1] + mat[i - 1][j - 1]
    
    def get(x, y):
        x = max(min(x, m), 0)
        y = max(min(y, n), 0)
        return P[x][y]

    ans = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            ans[i][j] = get(i + K + 1, j + K + 1) - get(i - K, j + K + 1) - get(i + K + 1, j - K) + get(i - K, j - K);
    return ans



def matrixBlockSum(self, mat: List[List[int]], k: int) -> List[List[int]]:
    m,n = len(mat),len(mat[0])
    p = [[0]*(1+n) for _ in range(1+m)]
    # 二维前缀和
    for i in range(1,m+1):
        for j in range(1,n+1):
            p[i][j] = p[i-1][j]+p[i][j-1]-p[i-1][j-1]+mat[i-1][j-1]

    # 任意矩形和
    def get(x1,y1,x2,y2):
        return p[x2][y2] - p[x2][y1-1] - p[x1-1][y2] + p[x1-1][y1-1]

    # 计算基于i,j的区域和
    res = []
    for i in range(1,m+1):
        tmp = []
        for j in range(1,n+1):
            q = get(max(i-k,1),max(j-k,1),min(i+k,m),min(j+k,n))
            tmp.append(q)
        res.append(tmp)
    return res


