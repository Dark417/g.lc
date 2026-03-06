"""
090.90 Subsets II
子集 II

Given a collection of integers that might contain duplicates, nums, 
return all possible subsets (the power set).

Note: The solution set must not contain duplicate subsets.

Example:

Input: [1,2,2]
Output:
[
  [2],
  [1],
  [1,2,2],
  [2,2],
  [1,2],
  []
]



"""

# D
def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
    a = [[]]
    for i in nums:
        for l in range(len(a)):
            x = a[l] + [i]
            x.sort()
            if x not in a:
                if a[l] == []:
                    a.append([i])
                else:
                    a.append(x)
    return a



# 改 not working
# def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
#     res = [[]]
#     for num in sorted(nums):
#         res += [item+[num] for item in res]
#     return res



def subsetsWithDup(self, nums):
    res = [[]]
    nums.sort()
    for num in nums: 	# for el in sorted(nums):
        res += [ i + [num] for i in res if i + [num] not in res]
    return res



return [list(subset) for subset in set(tuple(itertools.compress(sorted(nums), bits)) for bits in itertools.product(range(2), repeat=len(nums)))]


def subsetsWithDup(self, S):
    res = [[]]
    S.sort()
    for i in range(len(S)):
        if i == 0 or S[i] != S[i - 1]:
            l = len(res)
        for j in range(len(res) - l, len(res)):
            res.append(res[j] + [S[i]])
    return res


def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
    nums.sort()
    res=[[]]
    for i in range(len(nums)):
        if(i==0 or nums[i]!=nums[i-1]):
            l=len(res)
            for t in range(len(res)):
                res.append(res[t]+[nums[i]])
        else:
            p=len(res)
            for t in range(l,len(res)):
                res.append(res[t]+[nums[i]])
            l=p
    return res


def subsetsWithDup(self, nums):
    if not nums:
        return []
    nums.sort()
    res, cur = [[]], []
    for i in range(len(nums)):
        if i > 0 and nums[i] == nums[i-1]:
            cur = [item + [nums[i]] for item in cur]
        else:
            cur = [item + [nums[i]] for item in res]
        res += cur
    return res


def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
    superset = [[]]
    counts = collections.Counter(nums)
    for num, repeats in counts.items():
        new_subsets = []
        for subset in superset:
            new_subsets.extend([[num] * i + subset for i in range(1, repeats + 1)])
        superset.extend(new_subsets)
    return superset


# caikehe
# DFS  
def subsetsWithDup(self, nums):
    res = []
    nums.sort()
    self.dfs(nums, 0, [], res)
    return res
    
def dfs(self, nums, index, path, res):
    res.append(path)
    for i in xrange(index, len(nums)):
        if i > index and nums[i] == nums[i-1]:
            continue
        self.dfs(nums, i+1, path+[nums[i]], res)



def subsetsWithDup(self, nums):
    nums, result, pos = sorted(nums), [[]], {}
    for n in nums:
        start, l = pos.get(n, 0), len(result)
        result += [r + [n] for r in result[start:]]
        pos[n] = l
    return result


def subsetsWithDup(self, nums):
    nums.sort()
    res = [[]]
    for i in nums:
        res += [r+[i] for r in res]
    dic={}
    for i in res:
        dic[str(i)] = 0
    res=[]
    for key in dic:
        res.append(eval(key))
    return res


def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
    res = {tuple()}
    for n in sorted(nums):
        res |= {a + (n, ) for a in res}
    return res



# chn
def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
    res = []
    n = len(nums)
    nums.sort()
    def helper(idx, tmp):
        res.append(tmp)
        for i in range(idx, n):
            if i > idx and nums[i] == nums[i-1]:
                continue
            helper(i+1, tmp + [nums[i]])
    helper(0, [])
    return res


def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
    if not nums: return []
    nums.sort()
    res = [[]]
    cur = []
    for i in range(len(nums)):
        if i > 0 and nums[i - 1] == nums[i]:
            cur = [tmp + [nums[i]] for tmp in cur]
        else:
            cur = [tmp + [nums[i]] for tmp in res]
        res += cur
    return res










