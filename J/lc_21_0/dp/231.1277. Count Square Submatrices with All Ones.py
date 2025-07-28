"""
231.1277. Count Square Submatrices with All Ones




Given a m * n matrix of ones and zeros, return how many square submatrices have all ones.

 

Example 1:

Input: matrix =
[
  [0,1,1,1],
  [1,1,1,1],
  [0,1,1,1]
]
Output: 15
Explanation: 
There are 10 squares of side 1.
There are 4 squares of side 2.
There is  1 square of side 3.
Total number of squares = 10 + 4 + 1 = 15.
Example 2:

Input: matrix = 
[
  [1,0,1],
  [1,1,0],
  [1,1,0]
]
Output: 7
Explanation: 
There are 6 squares of side 1.  
There is 1 square of side 2. 
Total number of squares = 6 + 1 = 7.
 

Constraints:

1 <= arr.length <= 300
1 <= arr[0].length <= 300
0 <= arr[i][j] <= 1


"""


def countSquares(self, A):
    for i in xrange(1, len(A)):
        for j in xrange(1, len(A[0])):
            A[i][j] *= min(A[i - 1][j], A[i][j - 1], A[i - 1][j - 1]) + 1
    return sum(map(sum, A))




# official
def countSquares(self, matrix: List[List[int]]) -> int:
    m, n = len(matrix), len(matrix[0])
    f = [[0] * n for _ in range(m)]
    ans = 0
    for i in range(m):
        for j in range(n):
            if i == 0 or j == 0:
                f[i][j] = matrix[i][j]
            elif matrix[i][j] == 0:
                f[i][j] = 0
            else:
                f[i][j] = min(f[i][j - 1], f[i - 1][j], f[i - 1][j - 1]) + 1
            ans += f[i][j]
    return ans




# https://leetcode-cn.com/problems/count-square-submatrices-with-all-ones/solution/bu-yi-yang-de-si-lu-bao-li-qian-zhui-he-er-fen-by-/
# binary search























def countSquares(self, matrix: List[List[int]]) -> int:
    r, c = len(matrix), len(matrix[0])
    res = 0
    for l in range(1, min(r, c)):
        for i in range(r-l):
            for j in range(c-l):
                f = 1
                for m in range(i+l):
                    for n in range(j+l)
                        if matrix[m][n]:
                            
    return res



































