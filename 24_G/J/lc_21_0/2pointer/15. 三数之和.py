# 15. 三数之和

# official
def threeSum(self, nums: List[int]) -> List[List[int]]:
    n = len(nums)
    nums.sort()
    ans = list()
    
    for first in range(n):
        if first > 0 and nums[first] == nums[first - 1]:
            continue
        third = n - 1
        target = -nums[first]
        for second in range(first + 1, n):
            if second > first + 1 and nums[second] == nums[second - 1]:
                continue
            while second < third and nums[second] + nums[third] > target:
                third -= 1
			if second == third:
                break
            if nums[second] + nums[third] == target:
                ans.append([nums[first], nums[second], nums[third]])
    return ans



def threeSum(self, nums: List[int]) -> List[List[int]]:
    nums.sort()
    ans = set()
    for i,v in enumerate(nums):
        self.twoSum(nums[i+1:],-v,ans)
    return ans

def twoSum(self,nums,target,ans):
    d = {}
    for i,v in enumerate(nums):
        if target-v in d:
            ans.add((v,target-v,-target)) #3sum wants the numbers, while 2sum wanted the indices
        d[v] = i


# deduplicate by pointer
def threeSum(self, nums):
    res = []
    nums.sort()
    for i in xrange(len(nums)-2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        l, r = i+1, len(nums)-1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l +=1 
            elif s > 0:
                r -= 1
            else:
                res.append((nums[i], nums[l], nums[r]))
                while l < r and nums[l] == nums[l+1]:
                    l += 1
                while l < r and nums[r] == nums[r-1]:
                    r -= 1
                l += 1; r -= 1
    return res


# set
def threeSum(self, nums: List[int]) -> List[List[int]]:
    nums = sorted(nums)
    result = set()
    for i in range(len(nums)): 
        l = i + 1
        r = len(nums) - 1
        target = 0 - nums[i]
        while l < r:
            if nums[l] + nums[r] == target:
                result.add((nums[i], nums[l], nums[r]))
                l += 1
                r -= 1
            elif nums[l] + nums[r] < target:
                l += 1
            else:
                r -= 1
    return list(result)




from itertools import combinations
class Solution:
    def threeSum(self, n: List[int]) -> List[List[int]]:
    	n.sort()
    	D, S = {j:i for i,j in enumerate(n)}, set()
    	for [(a,i),(b,j)] in combinations(zip(n,range(len(n))),2):
    		if -(a+b) in D and D[-(a+b)] > j: S.add((a,b,-(a+b)))
    	return S


from itertools import combinations
class Solution:
    def threeSum(self, n: List[int]) -> List[List[int]]:
    	n.sort()
    	N, S = [[],[],0,0,[]], set()
    	for i in n: N[(i>0)-(i<0)].append(i)
    	for i in [1,-1]: N[2*i] = set(N[-i])
    	if len(N[0]) >= 3: S.add((0,0,0))
    	if len(N[0]) != 0:
    		for i in N[1]:
    			if -i in N[2]: S.add((i,0,-i))
    	for i in [1,-1]:
    		for [a,b] in combinations(N[i],2):
    			if -(a+b) in N[2*i]: S.add((a,b,-(a+b)))
    	return S


# D
def threeSum(self, nums: List[int]) -> List[List[int]]:
    res = []
    for i in range(len(nums)-2):
        s = -nums[i]
        dc = {}
        for j in range(i+1, len(nums)):
            if s - nums[j] in dc:
                if sorted([nums[i], nums[j], s - nums[j]]) not in res:
                    res.append(sorted([nums[i], nums[j], s - nums[j]]))
            dc[nums[j]] = s - nums[j]
    return res



def threeSum(self, nums: List[int]) -> List[List[int]]:
    n = len(nums)
    nums.sort()
    ans = list()
    
    # 枚举 a
    for first in range(n):
        # 需要和上一次枚举的数不相同
        if first > 0 and nums[first] == nums[first - 1]:
            continue
        # c 对应的指针初始指向数组的最右端
        third = n - 1
        target = -nums[first]
        # 枚举 b
        for second in range(first + 1, n):
            # 需要和上一次枚举的数不相同
            if second > first + 1 and nums[second] == nums[second - 1]:
                continue
            # 需要保证 b 的指针在 c 的指针的左侧
            while second < third and nums[second] + nums[third] > target:
                third -= 1
            # 如果指针重合，随着 b 后续的增加
            # 就不会有满足 a+b+c=0 并且 b<c 的 c 了，可以退出循环
            if second == third:
                break
            if nums[second] + nums[third] == target:
                ans.append([nums[first], nums[second], nums[third]])
    
    return ans























































