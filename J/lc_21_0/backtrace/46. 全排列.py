"""
078.46. Permutations
全排列

Given a collection of distinct integers, return all possible permutations.

Example:

Input: [1,2,3]
Output:
[
  [1,2,3],
  [1,3,2],
  [2,1,3],
  [2,3,1],
  [3,1,2],
  [3,2,1]
]

"""




# Stafen
def permute(self, nums):
    return [[n] + p
            for i, n in enumerate(nums)
            for p in self.permute(nums[:i] + nums[i+1:])] or [[]]


def permute(self, nums):
    return nums and [p[:i] + [nums[0]] + p[i:]
                     for p in self.permute(nums[1:])
                     for i in range(len(nums))] or [[]]


def permute(self, nums):
    return reduce(lambda P, n: [p[:i] + [n] + p[i:]
                                for p in P for i in range(len(p)+1)],
                  nums, [[]])


def permute(self, nums):
	return list(itertools.permutations(nums))
    return map(list, itertools.permutations(nums))
    	permute = lambda self, nums: list(map(list, itertools.permutations(nums)))


return [p[:i]+[nums[0]]+p[i:] 
            for i in range(len(nums)) # this line is 1st
            for p in self.permute(nums[1:]) #this line is 2ed
           ]or[[]]



def permute(self, nums: List[int]) -> List[List[int]]:
    return [
        p[:i] + [nums[0]] + p[i:]
        for i in range(len(nums))
        for p in self.permute(nums[1:])
    ]  or [[]]



# 1
# caikehe
# DFS
def permute(self, nums):
    res = []
    self.dfs(nums, [], res)
    return res
    
def dfs(self, nums, path, res):
    if not nums:
        res.append(path)
        return
    for i in xrange(len(nums)):
    	self.dfs(nums[:i] + nums[i+1:], path+[nums[i]], res)



def permute(self, nums: List[int]) -> List[List[int]]:
    def backtrack(nums, tmp):
        # nonlocal res  # not needed in local but online
        if not nums:
            res.append(tmp)
            return 
        for i in range(len(nums)):
            backtrack(nums[:i] + nums[i+1:], tmp + [nums[i]])
    res = []
    backtrack(nums, [])
    return res



def dfs(self, nums, res, line):
    if not nums:
        res.append(line)
        return
    for i, num in enumerate(nums):
        line.append(num)
        self.dfs(nums[:i]+nums[i+1:], res, line)
        line.pop()

def permute(self, nums):
    res = []
    self.dfs(nums, res, [])
    return res




# zhou
def permute(self, nums):
    self.res = []
    self.dfs(nums, [])
    return self.res
    
def dfs(self, nums, temp):
    if len(nums) == len(temp):
        self.res.append(temp[:])
        return
    
    for i in range(len(nums)):
        if nums[i] in temp: continue
        temp.append(nums[i])
        self.dfs(nums, temp)
        temp.pop()


def permute(self, nums: List[int]) -> List[List[int]]:
    visited = set()
    res = []
    self.backtracking(res,visited,[],nums)
    return res
    
def backtracking(self,res,visited,subset,nums):
    if len(subset) == len(nums):
        res.append(subset)
    for i in range(len(nums)):
        if i not in visited:
            visited.add(i)
            self.backtracking(res,visited,subset+[nums[i]],nums)
            visited.remove(i)



def permute(self, nums):
    def gen(nums):
        n = len(nums)
        if n == 0 : yield []
        else:
            for i in range(n):
                for cc in gen(nums[:i] + nums[i+1:]):
                #for cc in gen(nums[i+1:] + nums[:i]):
                    yield [nums[i]] + cc
                    # yield cc + [nums[i]]
    return list(gen(nums))



# recursion ! nb
def permute(self, nums):
    if len(nums) == 1:
        return [nums]
    result = []
    for i in range(len(nums)):
        others = nums[:i] + nums[i+1:]
        other_permutations = self.permute(others)
        for permutation in other_permutations:
            result.append([nums[i]] + permutation)
    return result



def permute(self, nums):
    perms = [[]]   
    for n in nums:
        new_perms = []
        for perm in perms:
            for i in xrange(len(perm)+1):   
                new_perms.append(perm[:i] + [n] + perm[i:])   ###insert n
        perms = new_perms
    return perms





def permute(self, nums):
    def backtrack(first = 0):
        if first == n:  
            res.append(nums[:])
        for i in range(first, n):
            nums[first], nums[i] = nums[i], nums[first]
            backtrack(first + 1)
            nums[first], nums[i] = nums[i], nums[first]
    
    n = len(nums)
    res = []
    backtrack()
    return res





# liweiwei
# 1
from typing import List

class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        def dfs(nums, size, depth, path, used, res):
            if depth == size:
			    res.append(path[:])
			    return

            for i in range(size):
                if not used[i]:
                    used[i] = True
                    path.append(nums[i])

                    dfs(nums, size, depth + 1, path, used, res)

                    used[i] = False
                    path.pop()

        size = len(nums)
        if len(nums) == 0:
            return []

        used = [False for _ in range(size)]
        res = []
        dfs(nums, size, 0, [], used, res)
        return res


if __name__ == '__main__':
    nums = [1, 2, 3]
    solution = Solution()
    res = solution.permute(nums)
    print(res)



# 2
from typing import List
class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        def dfs(nums, size, depth, path, state, res):
            if depth == size:
                res.append(path)
                return

            for i in range(size):
                if ((state >> i) & 1) == 0:
                    dfs(nums, size, depth + 1, path + [nums[i]], state ^ (1 << i), res)

        size = len(nums)
        if size == 0:
            return []

        state = 0
        res = []
        dfs(nums, size, 0, [], state, res)
        return res


# 3
from typing import List


class Solution:

    def permute(self, nums: List[int]) -> List[List[int]]:
        def dfs(nums, size, depth, hash_set, path, res):
            if depth == size:
                res.append(path[:])
                return

            for i in range(size):
                if not nums[i] in hash_set:
                    hash_set.add(nums[i])
                    path.append(nums[i])

                    dfs(nums, size, depth + 1, hash_set, path, res)
                    path.pop()
                    hash_set.remove(nums[i])

        size = len(nums)
        if size == 0:
            return []
        res = []
        path = []
        hash_set = set()
        dfs(nums, size, 0, hash_set, path, res)
        return res


# 4
from typing import List
class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        def dfs(nums, size, depth, path, used, res):
            if depth == size:
                res.append(path[:])
                return

            for i in range(size):
                if ((used >> i) & 1) == 0:
                    used ^= (1 << i)
                    path.append(nums[i])

                    dfs(nums, size, depth + 1, path, used, res)

                    used ^= (1 << i)
                    path.pop()

        size = len(nums)
        if size == 0:
            return []
        state = 0
        res = []
        dfs(nums, size, 0, [], state, res)
        return res







# comment
def permute(self, nums: List[int]) -> List[List[int]]:
    n = len(nums)
    ans_temp = [0] * n  #ans_temp存放每一次找到的结果
    ans = []            #存放最终的答案
    if n == 0:          #若为空数组，返回[[]]
        ans.append([])
        return ans
    else:               #process进行处理，答案放进ans
        self.process(nums,ans_temp,0,n,' ',ans)
        return ans


def process(self,nums,ans_temp,i,n,x,ans): #nums是待选择的数组，每深一层会减少一个，i是当前找索引为i的元素，n是数组总长度，x是上一层选出来的数，即i-1处的数。
    if i == n:        #已经遍历结束了
        ans_temp[n-1] = x  #最后一个元素加上，ans_temp数组即为一个解
        ttemp = []
        ttemp[:] = ans_temp[:] #使用ttemp数组来保存解，因为直接将ans_temp加入，会在回溯时候，ans_temp改变导致ans中的解也跟着变。
        ans.append(ttemp)
    else:
        temp = []  
        temp[:] = nums[:]  #为避免回溯同样问题，不对nums修改，使用temp来复制nums
        if x == ' ':    #刚开始，无需处理上层数据
            pass
        else:
            ans_temp[i-1] = x   #把上层数据放在它的位置
            temp.remove(x)   #将上层选过的数据删掉
        for y in temp: #遍历剩余的数据，相当于每种都选了一遍
            self.process(temp,ans_temp,i+1,n,y,ans)  #递归过程，深度优先遍历，temp变成新的nums。







