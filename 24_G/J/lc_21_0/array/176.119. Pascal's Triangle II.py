"""
176.119. Pascal's Triangle II
杨辉三角 II


Given a non-negative index k where k ≤ 33, return the kth index row of the Pascal's triangle.

Note that the row index starts from 0.


In Pascal's triangle, each number is the sum of the two numbers directly above it.

Example:

Input: 3
Output: [1,3,3,1]
Follow up:

Could you optimize your algorithm to use only O(k) extra space?




"""


def getRow(self, rowIndex: int) -> List[int]:
    cur = [1]
    for k in range(0, rowIndex):
        a,b = [0]+cur, cur+[0]
        res = [a[i]+b[i] for i in range(len(a))]
        cur = res
    return cur


def getRow(rowIndex):
    pascal = [1]*(rowIndex + 1)
    for i in range(2,rowIndex+1):
        for j in range(i-1,0,-1):
            pascal[j] += pascal[j-1]
    return pascal


def getRow(rowIndex):
    rt=[1]*(rowIndex+1)
    for i in range(2, rowIndex+1):
        for j in range(1, i):
            rt[i-j]+=rt[i-j-1]
    return rt



def getRow(self, rowIndex):
    row = [1]
    for _ in range(rowIndex):
        row = [x + y for x, y in zip([0]+row, row+[0])]
    return row

















































