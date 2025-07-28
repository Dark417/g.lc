"""
080.78. Subsets
子集

Given a set of distinct integers, nums, return all possible subsets (the power set).

Note: The solution set must not contain duplicate subsets.

Example:

Input: nums = [1,2,3]
Output:
[
  [3],
  [1],
  [2],
  [1,2,3],
  [1,3],
  [2,3],
  [1,2],
  []
]



"""


# 4th
def subsets(self, nums):
    res = []

    def select(c, cur, i):
        if len(cur) == c:
            res.append(list(cur))
            return
        if i >= len(nums):
            return
        cur.append(nums[i])
        select(c, cur, i + 1)
        cur.pop()
        select(c, cur, i + 1)

    for j in range(len(nums) + 1):
        select(j, [], 0)
    return res

    
# D
def subsets(self, nums: List[int]) -> List[List[int]]:
    a = [[]]
    for i in nums:
        for l in range(len(a)):
            if a[l] == []:
                a.append([i])
            else:
                a.append(a[l] + [i])
    return a

# Iteratively
def subsets(self, nums):
    res = [[]]
    for num in sorted(nums):
        res += [item+[num] for item in res]
    return res




# caikehe
# DFS recursively 
def subsets1(self, nums):
    res = []
    self.dfs(sorted(nums), 0, [], res)
    return res
    
def dfs(self, nums, index, path, res):
    res.append(path)
    for i in xrange(index, len(nums)):
        self.dfs(nums, i+1, path+[nums[i]], res)


    



# lee
def subsets(self, nums):
    return reduce(lambda L, ele: L + [l + [ele] for l in L], nums, [[]])

def subsets(self, nums):
    [[x for x in l if x is not None] for l in itertools.product(*zip(nums, [None] * len(nums)))]

def subsets(self, nums):
    [l for n in range(len(nums) + 1) for l in itertools.combinations(nums, n)]
    yield from itertools.chain.from_iterable(itertools.combinations(nums, x) for x in range(len(nums) + 1))
    [l for n in range(len(nums) + 1) for l in itertools.combinations(nums, n)]
    {itertools.compress(nums, bits) for bits in itertools.product(range(2), repeat=len(nums))}



# Stefam
return reduce(lambda subsets, n: subsets + [s+[n] for s in subsets], nums, [[]])

return [s for n in range(len(nums)+1)
            for s in itertools.combinations(nums, n)]

return [[nums[i] for i in range(len(nums)) if mask >> i & 1]
            for mask in range(2 ** len(nums))]



# powcai
def subsets(self, nums: List[int]) -> List[List[int]]:
    res = []
    for i in range(len(nums)+1):
        for tmp in itertools.combinations(nums, i):
            res.append(tmp)
    return res




# official
# https://leetcode-cn.com/problems/subsets/solution/zi-ji-by-leetcode/
# recursion
def subsets(self, nums: List[int]) -> List[List[int]]:
    n = len(nums)
    output = [[]]
    
    for num in nums:
        output += [curr + [num] for curr in output]
    
    return output



def subsets(self, nums: List[int]) -> List[List[int]]:
    res = []
    n = len(nums)
    
    def helper(i, tmp):
        res.append(tmp)
        for j in range(i, n):
            helper(j + 1,tmp + [nums[j]] )
    helper(0, [])
    return res  




# backtracking
def subsets(self, nums: List[int]) -> List[List[int]]:
    def backtrack(first = 0, curr = []):
        if len(curr) == k:  
            output.append(curr[:])
        for i in range(first, n):
            curr.append(nums[i])
            backtrack(i + 1, curr)
            curr.pop()
            
            backtrack(i + 1, curr+[nums[i]])
            
    output = []
    n = len(nums)
    for k in range(n + 1):
        backtrack()
    return output










# bit mask
for i in range(2**n, 2**(n + 1)):
    # generate bitmask, from 0..00 to 1..11
    bitmask = bin(i)[3:]

def subsets(self, nums: List[int]) -> List[List[int]]:
        n = len(nums)
        output = []
        
        for i in range(2**n, 2**(n + 1)):
            # generate bitmask, from 0..00 to 1..11
            bitmask = bin(i)[3:]
            
            # append subset corresponding to that bitmask
            output.append([nums[j] for j in range(n) if bitmask[j] == '1'])
        
        return output


def subsets(self, nums):
    length = len(nums)
    res = []
    for i in range(2**length):
        index = length-1
        temp = []
        while index > -1:
            if i % 2 == 1:
                temp.append(nums[index])
            index -= 1
            i = i >> 1
        res.append(temp)
    return res



# Bit Manipulation    
def subsets2(self, nums):
    res = []
    nums.sort()
    for i in xrange(1<<len(nums)):
        tmp = []
        for j in xrange(len(nums)):
            if i & 1 << j:  # if i >> j & 1:
                tmp.append(nums[j])
        res.append(tmp)
    return res


































