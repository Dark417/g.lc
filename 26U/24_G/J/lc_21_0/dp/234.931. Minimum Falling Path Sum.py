"""
234.931. Minimum Falling Path Sum
下降路径最小和

Given a square array of integers A, we want the minimum sum of a falling path through A.

A falling path starts at any element in the first row, and chooses one element from each row.  The next row's choice must be in a column that is different from the previous row's column by at most one.

 

Example 1:

Input: [[1,2,3],[4,5,6],[7,8,9]]
Output: 12
Explanation: 
The possible falling paths are:
[1,4,7], [1,4,8], [1,5,7], [1,5,8], [1,5,9]
[2,4,7], [2,4,8], [2,5,7], [2,5,8], [2,5,9], [2,6,8], [2,6,9]
[3,5,7], [3,5,8], [3,5,9], [3,6,8], [3,6,9]
The falling path with the smallest sum is [1,4,7], so the answer is 12.

 

Constraints:

1 <= A.length == A[0].length <= 100
-100 <= A[i][j] <= 100
"""



def minFallingPathSum(self, A):
    while len(A) >= 2:
        row = A.pop()            
        for i in xrange(len(row)):
            A[-1][i] += min(row[max(0,i-1): min(len(row), i+2)])
    return min(A[0])


def minFallingPathSum(self, A: List[List[int]]) -> int:
    for l in range(1, len(A)):
        for n in range(len(A[l])):
            
            if len(A[l]) == 1:
                A[l][n] = A[l-1][n]
            else:
                if n == 0:
                    A[l][n] += min(A[l-1][n], A[l-1][n+1])
                elif n == len(A[l])-1:
                    A[l][n] += min(A[l-1][n-1], A[l-1][n])
                else:
                    A[l][n] += min(A[l-1][n-1], A[l-1][n], A[l-1][n+1])
    return min(A[-1])




def minFallingPathSum(self, A):
    dp = A[0]
    for row in A[1:]:
        dp = [value + min([dp[c], dp[max(c - 1, 0)], dp[min(len(A) - 1, c + 1)]]) for c, value in enumerate(row)]
    return min(dp)



def minFallingPathSum(self, A):
    for i in range(1, len(A)):
        for j in range(len(A[0])):
            topleft = A[i-1][j-1] if j-1>=0 else float('inf')
            topright = A[i-1][j+1] if j+1<len(A[0]) else float('inf')
            A[i][j] += min(topleft, topright, A[i-1][j])
       
    return min(A[-1])
















































































