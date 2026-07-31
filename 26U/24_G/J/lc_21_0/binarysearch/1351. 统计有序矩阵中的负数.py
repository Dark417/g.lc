# 1351. 统计有序矩阵中的负数



def countNegatives(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    c = 0
    for i in range(m):
        if grid[i][0] < 0:
            c += n * (m - i)
            return c
        
        l, r = 0, n - 1   # n
        while l <= r:
            mid = l + (r - l) //2
            if grid[i][mid] < 0:
                r = mid - 1		# mid
            else:
                l = mid + 1                    
            
        c += n - l
    return c



def countNegatives(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    c = 0
    r = n
    for i in range(m):
        if grid[i][0] < 0:
            c += n * (m - i)
            return c
        
        l = 0
        while l < r:
            mid = l + (r - l) //2
            if grid[i][mid] < 0:
                r = mid 
            else:
                l = mid + 1                
        c += n - l
        r = l
    return c


def countNegatives(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    c = 0
    p = n
    for i in range(m):
        for j in range(p):
            if grid[i][j] < 0:
                c += (p - j) * (m - i)
                p = j
                break
    return c

        

def countNegatives(self, grid: List[List[int]]) -> int:
    m, n = len(grid[0]),len(grid)
    res,ind = 0,m
    for i in range(n):
        if ind==0: break
        if grid[i][ind-1]>=0: continue
        cnt = 0;
        while ind-1>=0  and grid[i][ind-1]<0:
            ind -= 1
            cnt += 1
        res += cnt*(n-i)
    return res	







def countNegatives(self, grid: List[List[int]]) -> int:
    m, n = len(grid[0]),len(grid)
    res,ind = 0,m
    for i in range(n):
        if ind==0: break
        if grid[i][ind-1]>=0: continue
        left, right= 0, ind
        while left<right:
            mid = left+(right-left)//2
            if grid[i][mid]>=0: left = mid + 1
            else: right = mid
        res += (ind-left)*(n-i)
        ind = left
    return res


def countNegatives(self, grid: List[List[int]]) -> int:
    m, n = len(grid[0]),len(grid)
    res,ind = 0,m
    for i in range(n):
        if ind==0: break
        if grid[i][ind-1]>=0: continue
        left, right= 0, ind
        while left<right:
            mid = left+(right-left)//2
            if grid[i][mid]>=0: left = mid + 1
            else: right = mid
        res += (ind-left)*(n-i)
        ind = left
    return res










from itertools import chain
class Solution:
    def countNegatives(self, grid: List[List[int]]) -> int:
        return len(list(filter(lambda x:x<0,chain(*grid))))




























