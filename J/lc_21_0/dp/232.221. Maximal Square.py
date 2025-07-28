"""
232.221. Maximal Square

Given a 2D binary matrix filled with 0's and 1's, find the largest square containing only 1's and return its area.

Example:

Input: 

1 0 1 0 0
1 0 1 1 1
1 1 1 1 1
1 0 0 1 0

Output: 4


"""

matrix[i][j] = min(matrix[i-1][j-1], matrix[i-1][j], matrix[i][j-1]
                ) + 1 if i and j and matrix[i][j] == "1" else int(matrix[i][j])



# https://leetcode-cn.com/problems/maximal-square/solution/fen-xiang-yi-ge-bu-yong-dong-tai-gui-hua-cai-yong-/
def getWidth(self,num):  #步骤3：求一个数中连续最多的1
    w=0
    while num>0:
        num&=num<<1
        w+=1
    return w
def maximalSquare(self, matrix: List[List[str]]) -> int:
    nums=[int(''.join(n),base=2) for n in matrix]  #步骤1：每一行当作二进制数
    res,n=0,len(nums)
    for i in range(n):   #步骤2：枚举所有的组合，temp存储相与的结果
        temp=nums[i]
        for j in range(i,n):
            temp&=nums[j]
            w=self.getWidth(temp)
            h=j-i+1
            res=max(res,min(w,h))
    return res*res


def getWidth(self,num):  #步骤3：求一个数中连续最多的1
    w=0
    while num>0:
        num&=num<<1
        w+=1
    return w
def maximalSquare(self, matrix: List[List[str]]) -> int:
    nums=[int(''.join(n),base=2) for n in matrix]  #步骤1：每一行当作二进制数
    res,n=0,len(nums)
    for i in range(n):   #步骤2：枚举所有的组合，temp存储相与的结果
        temp=nums[i]
        for j in range(i,n):
            temp&=nums[j]
            if self.getWidth(temp)<j-i+1:
                break
            res=max(res,j-i+1)
    return res*res







def maximalSquare(self, A):
    for i in range(len(A)):
        for j in range(len(A[i])):
            A[i][j] = int(A[i][j])
            if A[i][j] and i and j:
                A[i][j] = min(A[i-1][j], A[i-1][j-1], A[i][j-1]) + 1
    return len(A) and max(map(max, A)) ** 2


def maximalSquare(self, A):
    for i, r in enumerate(A):
        r = A[i] = map(int, r)
        for j, c in enumerate(r):
            if i * j * c:
                r[j] = min(A[i-1][j], r[j-1], A[i-1][j-1]) + 1
    return max(map(max, A + [[0]])) ** 2



def maximalSquare(self, A):
    area = 0
    if A:
        p = [0] * len(A[0])
        for row in A:
            s = map(int, row)
            for j, c in enumerate(s[1:], 1):
                s[j] *= min(p[j-1], p[j], s[j-1]) + 1
            area = max(area, max(s) ** 2)
            p = s
    return area



def maximalSquare(self, matrix: List[List[str]]) -> int:  
    rows, cols = len(matrix), len(matrix[0]) if matrix else 0
    d = defaultdict(lambda:0)
    ans = 0
    
    """
    d[(r,c)] is the side-len of the maximal sq at matrix[r][c]
    """
    
    for t in product(range(rows), range(cols)):
        
        r,c = t
        d[t] = int(matrix[r][c]) and \
            1 + min(d[(r-1,c-1)], \
                    d[(r-1,c)], \
                    d[(r,c-1)])
        ans = max(ans, d[t])
    
    return ans**2


# official
# brute force
def maximalSquare(self, matrix: List[List[str]]) -> int:
    if len(matrix) == 0 or len(matrix[0]) == 0:
        return 0
    
    maxSide = 0
    rows, columns = len(matrix), len(matrix[0])
    for i in range(rows):
        for j in range(columns):
            if matrix[i][j] == '1':
                # 遇到一个 1 作为正方形的左上角
                maxSide = max(maxSide, 1)
                # 计算可能的最大正方形边长
                currentMaxSide = min(rows - i, columns - j)
                for k in range(1, currentMaxSide):
                    # 判断新增的一行一列是否均为 1
                    flag = True
                    if matrix[i + k][j + k] == '0':
                        break
                    for m in range(k):
                        if matrix[i + k][j + m] == '0' or matrix[i + m][j + k] == '0':
                            flag = False
                            break
                    if flag:
                        maxSide = max(maxSide, k + 1)
                    else:
                        break
    
    maxSquare = maxSide * maxSide
    return maxSquare


# dp
def maximalSquare(self, matrix: List[List[str]]) -> int:
    if len(matrix) == 0 or len(matrix[0]) == 0:
        return 0
    
    maxSide = 0
    rows, columns = len(matrix), len(matrix[0])
    dp = [[0] * columns for _ in range(rows)]
    for i in range(rows):
        for j in range(columns):
            if matrix[i][j] == '1':
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                maxSide = max(maxSide, dp[i][j])
    
    #res = max(max(row) for row in dp)
    maxSquare = maxSide * maxSide
    return maxSquare















































