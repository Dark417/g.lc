"""
097.39. Combination Sum
组合总和


Given a set of candidate numbers (candidates) (without duplicates) and a target number 
(target), find all unique combinations in candidates where the candidate numbers sums to target.

The same repeated number may be chosen from candidates unlimited number of times.

Note:

All numbers (including target) will be positive integers.
The solution set must not contain duplicate combinations.
Example 1:

Input: candidates = [2,3,6,7], target = 7,
A solution set is:
[
  [7],
  [2,2,3]
]
Example 2:

Input: candidates = [2,3,5], target = 8,
A solution set is:
[
  [2,2,2,2],
  [2,3,3],
  [3,5]
]
"""


# dp https://leetcode.com/problems/combination-sum/discuss/937255/Python-3-or-DFSBacktracking-and-Two-DP-methods-or-Explanations


def combinationSum(self, candidates, target):
    def recursion(idx, res):
        if idx >= len(candidates) or res >= target:
            if res == target:
                ans.append(temp[:])
            return
        temp.append(candidates[idx])
        recursion(idx, res + candidates[idx]) 
        temp.pop()
        recursion(idx + 1, res)

    ans = []
    temp = []
    recursion(0, 0)
    return ans



def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
    def dfs(candidates, begin, size, path, res, target):
        if target < 0:
            return
        if target == 0:
            res.append(path)
            return

        for index in range(begin, size):
            dfs(candidates, index, size, path + [candidates[index]], res, target - candidates[index])

    size = len(candidates)
    if size == 0:
        return []
    path = []
    res = []
    dfs(candidates, 0, size, path, res, target)
    return res



def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
    def dfs(candidates, begin, size, path, res, target):
        if target == 0:
            res.append(path)
            return
        for index in range(begin, size):
            residue = target - candidates[index]
            if residue < 0:
                break
            dfs(candidates, index, size, path + [candidates[index]], res, residue)
    size = len(candidates)
    if size == 0:
        return []
    candidates.sort()
    path = []
    res = []
    dfs(candidates, 0, size, path, res, target)
    return res



def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
    candidates = sorted(candidates)
    ans = []
    def find(s, use, remain):
        for i in range(s, len(candidates)):
            c = candidates[i]
            if c == remain:
                ans.append(use + [c])
            if c < remain:
                find(i, use + [c], remain - c)
            if c > remain:
                return
    find(0, [], target)
    return ans


def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
    results = []
    def helper(i, path):
        if sum(path) == target:
            results.append(path[:])
            return 
        if sum(path) > target:
            return 
        for x in range(i, len(candidates)):
            path.append(candidates[x])
            helper(x, path)
            path.pop()
    helper(0, [])
    return results


# ~= begin / indx
def combinationSum(self, candidates, target):
    ret = []
    self.dfs(candidates, target, [], ret)
    return ret

def dfs(self, nums, target, path, ret):
    if target < 0:
        return 
    if target == 0:
        ret.append(path)
        return 
    for i in range(len(nums)):
        self.dfs(nums[i:], target-nums[i], path+[nums[i]], ret)


# ~~= begin / idx
def combinationSum(self, nums, target):
    res = []
    nums.sort()
    def dfs(left, path, idx):
        if not left: res.append(path[:])
        else:
            for i, val in enumerate(nums[idx:]):
                if val > left: 
                    break
                dfs(left - val, path + [val], idx + i)
    dfs(target, [], 0)
    return res


def combinationSum(self, candidates, target):
    res = []
    candidates.sort()
    
    def dfs(target, index, path):
        if target < 0:
            return  # backtracking
        if target == 0:
            res.append(path)
            return 
        for i in range(index, len(candidates)):
            dfs(target-candidates[i], i, path+[candidates[i]])
    
    dfs(target, 0, [])
    return res





def combinationSum(self, candidates, target):
    result = []
    candidates = sorted(candidates)
    def dfs(remain, stack):
        if remain == 0:
            result.append(stack)
            return 

        for item in candidates:
            if item > remain: break
            if stack and item < stack[-1]: continue
            else:
                dfs(remain - item, stack + [item])
    
    dfs(target, [])
    return result


# 223 232 322 重复
# def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
#     def dfs(cur, s):
#         if s == target:
#             self.res.append(cur)
#             return
#         for c in candidates:
#             if s + c <= target:
#                 dfs(cur + [c], s + c)
#             else:
#                 continue
            
#     self.res = []
#     dfs([], 0)
#     return self.res



# def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
#     def dfs(cur, s):
#         if s == target:
#             self.res.append(cur)
#         elif s < target:
#             for c in candidates:
#                 dfs(cur + [c], s + c)
#     self.res = []

#     dfs([], 0)
#     return self.res









def combinationSum(self, candidates, target):
    dp = [[[]] if j == 0 else [] for j in range(target + 1)]
    for candidate in candidates:
        for j in range(candidate, target + 1):
            dp[j] += [res + [candidate] for res in dp[j - candidate]]
    return dp[-1]




def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
    dict = {}
    for i in range(1,target+1):
        dict[i]=[]
    
    for i in range(1,target+1):
        for j in candidates:
            if i==j:
                dict[i].append([i])
            elif i>j:
                for k in dict[i-j]:
                    x = k[:]
                    x.append(j)
                    x.sort() # 升序，便于后续去重
                    if x not in dict[i]:
                        dict[i].append(x)

    return dict[target]
























