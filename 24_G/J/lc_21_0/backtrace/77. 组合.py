"""
096.77. Combinations
组合


Given two integers n and k, return all possible combinations of k numbers out of 1 ... n.

Example:

Input: n = 4, k = 2
Output:
[
  [2,4],
  [3,4],
  [2,3],
  [1,2],
  [1,3],
  [1,4],
]





"""

# D
def combine(self, n: int, k: int) -> List[List[int]]:
    def dfs(cur, start):
        if len(cur) == k:
            res.append(cur)
        else:
            for i in range(start+1, n+1):
                dfs(cur + [i], i)
    res = []
    if k!= 0 and n!=0:
        dfs([], 0)
    return res



# official
def combine(self, n: int, k: int) -> List[List[int]]:
    def backtrack(first = 1, curr = []):
        if len(curr) == k:  
            output.append(curr[:])
        for i in range(first, n + 1):
            curr.append(i)
            backtrack(i + 1, curr)
            curr.pop()
            
            backtrack(i + 1, curr+[i])

    output = []
    backtrack()
    return output





def combine(self, n: int, k: int) -> List[List[int]]:
    res = []
    self.backtrack(n, k, res, [], 1)
    return res

def backtrack(self, n, k, res, path, index):
    if len(path) == k:
        res.append(path)
        return
    # if index == n+1 or len(path) > k:
    #     return
    for i in range(index, n+1):
        self.backtrack(n, k, res, path+[i], i+1)





def combine(self, n, k):
    res = []
    self.dfs(xrange(1,n+1), k, 0, [], res)
    return res
    
def dfs(self, nums, k, index, path, res):
    if k == 0:
        res.append(path)
        return # backtracking 
    for i in xrange(index, len(nums)):
        self.dfs(nums, k-1, i+1, path+[nums[i]], res)



def combine(self, n, k):
    res = []
    self.dfs(range(1,n+1), k, [], res)
    return res
    
def dfs(self, nums, k, path, res):
    if k == 0:
        res.append(path)
        return
    if len(nums) >= k:
        for i in range(len(nums)):
            self.dfs(nums[i+1:], k-1, path+[nums[i]], res)
    return






def combine(self, n, k):
    self.ans = []
    nums = range(1, n+1)
    self.dfs(0, nums, [], k)
    return self.ans
def dfs(self, start, nums, valuelist, k):
    if k > len(nums) - start + 1: return
    elif k == 0:
        self.ans.append(valuelist)
        return
    for i in range(start, len(nums)):
        self.dfs(i+1, nums, valuelist + [nums[i]], k-1)







def combine(self, n: int, k: int) -> List[List[int]]:
    res = []
    nums = [i+1 for i in range(n)]
    self.dfs(nums,[],res,k, 0)
    return res

def dfs(self, nums, path ,res, target, index):
    if len(path) == target:
            res.append(path)
            return 
        
    for i in range(index, len(nums)-(target - len(path))+1 ):
        self.dfs(nums, path+[nums[i]], res, target, i+1)






# liweiwei
from typing import List
class Solution:
    def combine(self, n: int, k: int) -> List[List[int]]:
        if n <= 0 or k <= 0 or k > n:
            return []
        res = []
        self.__dfs(1, k, n, [], res)
        return res

    def __dfs(self, start, k, n, pre, res):
        if len(pre) == k:
            res.append(pre[:])
            return

        for i in range(start, n + 1):
            pre.append(i)
            self.__dfs(i + 1, k, n, pre, res)
            pre.pop()

# improved
def combine(self, n: int, k: int) -> List[List[int]]:
        # 特判
        if n <= 0 or k <= 0 or k > n:
            return []
        res = []
        self.__dfs(1, k, n, [], res)
        return res

    def __dfs(self, start, k, n, pre, res):
        if len(pre) == k:
            res.append(pre[:])
            return

        # 注意：这里 i 的上限是归纳得到的
        for i in range(start, n - (k - len(pre)) + 2):
            pre.append(i)
            self.__dfs(i + 1, k, n, pre, res)
            pre.pop()



def combine(self, n: int, k: int) -> List[List[int]]:
    def dfs(start: int, idx: int):
        for i in range(start, n + 1 - (k - 1 - idx)):
            option[idx] = i
            if idx == k - 1:
                ans.append(option[:])
            else:
                dfs(i + 1, idx + 1)

    ans = []
    option = [0] * k
    dfs(1, 0)
    return ans





from itertools import combinations
def combine(self, n, k):
    return list(combinations(range(1, n+1), k))


def combine(self, n, k):
    if k == 0:
        return [[]]
    return [pre + [i] for i in range(k, n+1) for pre in self.combine(i-1, k-1)]


def combine(self, n, k):
    combs = [[]]
    for _ in range(k):
        combs = [[i] + c for c in combs for i in range(1, c[0] if c else n+1)]
    return combs


def combine(self, n, k):
    return reduce(lambda C, _: [[i]+c for c in C for i in range(1, c[0] if c else n+1)],
                  range(k), [[]])




# 字典序 (二进制排序) 组合
def combine(self, n: int, k: int) -> List[List[int]]:
    nums = list(range(1, k + 1)) + [n + 1]
    output, j = [], 0
    while j < k:
        output.append(nums[:k])
        j = 0
        while j < k and nums[j + 1] == nums[j] + 1:
            nums[j] = j + 1
            j += 1
        nums[j] += 1
    return output






def combine(self, n, k):
    ans = []
    stack = []
    x = 1
    while True:
        l = len(stack)
        if l == k:
            ans.append(stack[:])
        if l == k or x > n - k + l + 1:
            if not stack:
                return ans
            x = stack.pop() + 1
        else:
            stack.append(x)
            x += 1


def combine(self, n, k):
    stack = []
    res = []
    l, x = 0, 1
    while True:
        
        if l == k:
            res.append(stack[:])
        if l == k or n-x+1 < k-l:
            if not stack:
                return res
            x = stack.pop() + 1
            l -= 1
        else:
            stack.append(x)
            x += 1
            l += 1

























