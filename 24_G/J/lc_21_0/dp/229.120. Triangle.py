"""
229.120. Triangle
三角形最小路径和


Given a triangle, find the minimum path sum from top to bottom. Each step you may move 
to adjacent numbers on the row below.

For example, given the following triangle

[
     [2],
    [3,4],
   [6,5,7],
  [4,1,8,3]
]
The minimum path sum from top to bottom is 11 (i.e., 2 + 3 + 5 + 1 = 11).

Note:

Bonus point if you are able to do this using only O(n) extra space, where n is the 
total number of rows in the triangle.

"""



def minimumTotal(self, triangle: List[List[int]]) -> int:
    if not triangle: return 0
    for l in range(1, len(triangle)):
        for i in range(len(triangle[l])):
            if i == 0:
                triangle[l][i] += triangle[l-1][0]
            elif i == len(triangle[l])-1:
                triangle[l][i] += triangle[l-1][-1]
            else:
                triangle[l][i] += min(triangle[l-1][i-1], triangle[l-1][i])
    return min(triangle[-1])


# caikehe
# O(n*n/2) space, top-down 
def minimumTotal1(self, triangle):
    if not triangle:
        return 
    res = [[0 for i in xrange(len(row))] for row in triangle]
    res[0][0] = triangle[0][0]
    for i in xrange(1, len(triangle)):
        for j in xrange(len(triangle[i])):
            if j == 0:
                res[i][j] = res[i-1][j] + triangle[i][j]
            elif j == len(triangle[i])-1:
                res[i][j] = res[i-1][j-1] + triangle[i][j]
            else:
                res[i][j] = min(res[i-1][j-1], res[i-1][j]) + triangle[i][j]
    return min(res[-1])
    
# Modify the original triangle, top-down
def minimumTotal2(self, triangle):
    if not triangle:
        return 
    for i in xrange(1, len(triangle)):
        for j in xrange(len(triangle[i])):
            if j == 0:
                triangle[i][j] += triangle[i-1][j]
            elif j == len(triangle[i])-1:
                triangle[i][j] += triangle[i-1][j-1]
            else:
                triangle[i][j] += min(triangle[i-1][j-1], triangle[i-1][j])
    return min(triangle[-1])
    
# Modify the original triangle, bottom-up
def minimumTotal3(self, triangle):
    if not triangle:
        return 
    for i in xrange(len(triangle)-2, -1, -1):
        for j in xrange(len(triangle[i])):
            triangle[i][j] += min(triangle[i+1][j], triangle[i+1][j+1])
    return triangle[0][0]

# bottom-up, O(n) space
def minimumTotal(self, triangle):
    if not triangle:
        return 
    res = triangle[-1]
    for i in xrange(len(triangle)-2, -1, -1):
        for j in xrange(len(triangle[i])):
            res[j] = min(res[j], res[j+1]) + triangle[i][j]
    return res[0]


# official
def minimumTotal(self, triangle: List[List[int]]) -> int:
    n = len(triangle)
    f = [[0] * n for _ in range(n)]
    f[0][0] = triangle[0][0]

    for i in range(1, n):
        f[i][0] = f[i - 1][0] + triangle[i][0]
        for j in range(1, i):
            f[i][j] = min(f[i - 1][j - 1], f[i - 1][j]) + triangle[i][j]
        f[i][i] = f[i - 1][i - 1] + triangle[i][i]
    
    return min(f[n - 1])



def minimumTotal(self, triangle: List[List[int]]) -> int:
    n = len(triangle)
    f = [[0] * n for _ in range(2)]
    f[0][0] = triangle[0][0]

    for i in range(1, n):
        curr, prev = i % 2, 1 - i % 2
        f[curr][0] = f[prev][0] + triangle[i][0]
        for j in range(1, i):
            f[curr][j] = min(f[prev][j - 1], f[prev][j]) + triangle[i][j]
        f[curr][i] = f[prev][i - 1] + triangle[i][i]
    
    return min(f[(n - 1) % 2])



def minimumTotal(self, triangle: List[List[int]]) -> int:
    n = len(triangle)
    f = [0] * n
    f[0] = triangle[0][0]

    for i in range(1, n):
        f[i] = f[i - 1] + triangle[i][i]
        for j in range(i - 1, 0, -1):
            f[j] = min(f[j - 1], f[j]) + triangle[i][j]
        f[0] += triangle[i][0]
    
    return min(f)




def minimumTotal(self, triangle: List[List[int]]) -> int:
    for r in range(len(triangle)-2,-1,-1):
        for c in range(len(triangle[r])):
            triangle[r][c]+=min(triangle[r+1][c:c+2])
    return triangle[0][0]



def minimumTotal(self, triangle: List[List[int]]) -> int:
	def rec(i, j):
		if i == len(triangle):
			return 0
		return min(rec(i+1, j), rec(i+1, j+1)) + triangle[i][j]
	return rec(0, 0)


def minimumTotal(self, triangle: List[List[int]]) -> int:
    def rec(i, j):
        if i == len(triangle):
            return 0
        memo[(i+1, j)] = rec(i+1, j)
        memo[(i+1, j+1)] = rec(i+1, j+1)
        return min(memo[(i+1, j)], memo[(i+1, j+1)]) + triangle[i][j]
    memo = {}
    return rec(0, 0)



def minimumTotal(self, triangle: List[List[int]]) -> int:
    def rec(i, j):
        if i == len(triangle):
            return 0
        try:
            if memo[(i, j)] != None:
                return memo[(i, j)]
        except:
            memo[(i+1, j)] = rec(i+1, j)
            memo[(i+1, j+1)] = rec(i+1, j+1)
            return min(memo[(i+1, j)], memo[(i+1, j+1)]) + triangle[i][j]
    memo = {}
    return rec(0, 0)




# this is a one liner for fun :)  Node that this creates a new triangle [::-1] was used, so unfortunately space was not k. 
def minimumTotal(self, triangle):

    return reduce(lambda x, y: [min(x[b], x[b+1])+y[b] for b in xrange(len(y))], triangle[::-1], [0]*(len(triangle)+1))[0]


# this is my original expended version of that one liner, somehow faster than that, achieved 44ms, but I guess the running time varies enough each time you submit, 
# so that the real difference is not significant
def minimumTotalExpended(self, triangle):

    triangle.append([0]*(len(triangle)+1))
    return reduce(lambda x, y: [min(x[b], x[b+1])+y[b] for b in xrange(len(y))], triangle[::-1])[0]


# further expend, in this one, no extra triangle was created, only one line each time, so space is k.
def minimumTotalDP(self, triangle):
    
    base=[0]*(len(triangle)+1)
    for i in xrange(len(triangle)-1, -1, -1):
        base=[min(base[b], base[b+1])+triangle[i][b] for b in xrange(i+1)]
    return base[0]



#recursive, top down, slower.  I think this is not well written, could be imporved much.
def minimumTotalRecurse(self, triangle):
    self.triangle=triangle
    self.cache=dict()
    return self.recurse(0,0) if triangle else 0

def recurse(self, level, i):
    if (level,i) in self.cache:
        return self.cache[(level,i)]

    if level==len(self.triangle)-1:
        return self.triangle[level][i]

    res=self.triangle[level][i]+min(self.recurse(level+1, i), self.recurse(level+1, i+1))
    self.cache[(level, i)]=res

    return res


# DP from top down, I wrote this one when I started learning programing.  Not a good piece for sure...speed was not bad though.
def minimumTotalTopDownDP(self, triangle):
    minSum=float('inf')
    if not triangle:
        return 0
    level1Sum=[triangle[0][0]]
    level2Sum=[]
    while len(triangle)>len(level1Sum):
        level2Sum=[triangle[len(level1Sum)][i]+min((level1Sum[i] if i < len(level1Sum) else float('inf')),(level1Sum[i-1] if i>=1 else float('inf')) ) \
        for i in xrange(len(level1Sum)+1)]
        level1Sum=level2Sum
        level2Sum=[]



# rec
def minimumTotal(self, triangle: List[List[int]]) -> int:
    def helper(row):
        if row == 0:
            return triangle[0]
        dp = [float('inf')] + helper(row - 1) + [float('inf')]
        curr_row = triangle[row]
        for i in range(len(triangle[row])):
            curr_row[i] += min(dp[i], dp[i + 1])
        return curr_row
    
    return min(helper(len(triangle) - 1))



# memoization
def minimumTotal(self, triangle):
    if not triangle:
        return 0
    
    def minimumTotalRecursive(arr, row, col):
        if row == len(arr):
            return 0
        else:
            ans = sys.maxint
            for j in (0, 1):
                new_col = col + j
                if 0 <= new_col < row + 1:
                    ans = min(ans, arr[row][new_col] + 
                              minimumTotalRecursive(arr, row + 1, new_col))
            return ans
    
    def minimumTotalMemoization(arr, row, col):
        if row == len(arr):
            return 0
        elif memoize[row][col] != None:
            return memoize[row][col]
        else:
            ans = sys.maxint
            for j in (0, 1):
                new_col = col + j
                if 0 <= new_col < row + 1:
                    ans = min(ans, arr[row][new_col] + 
                              minimumTotalMemoization(arr, row + 1, new_col))
            memoize[row][col] = ans
            return memoize[row][col]
    # Times out
    # return minimumTotalRecursive(triangle, 0, 0)
    memoize = [[None for _ in range(len(triangle[-1]) + 1)] for _ in range(len(triangle) + 1)]
    return minimumTotalMemoization(triangle, 0, 0)


















































