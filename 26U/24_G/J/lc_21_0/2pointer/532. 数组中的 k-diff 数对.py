# 532. 数组中的 k-diff 数对

def findPairs(self, nums: List[int], k: int) -> int:
	res = 0
	nums.sort()
	i = j = 0
	while i < len(nums) and j < len(nums):
		if i == j or nums[i] + k > nums[j]:
			j += 1
		elif nums[i] + k < nums[j]:
			i += 1
		else:
			res += 1
			i += 1
			while j < len(nums)-1 and nums[j] == nums[j+1]:
				j += 1
			j += 1
	return res



def findPairs(self, nums, k):
    res = 0
    c = collections.Counter(nums)
    for i in c:
        if k > 0 and i + k in c or k == 0 and c[i] > 1:
            res += 1
    return res




def findPairs(self, nums, k):
    count = Counter(nums)
    if k > 0:
        res = sum([i + k in count for i in count])
    else:
        res = sum([count[i] > 1 for i in count])
    return res



def findPairs(self, nums: List[int], k: int) -> int:
    if k<0:
        return 0
    saw, diff = set(), set()
    for i in nums:
        if i-k in saw:
            diff.add(i-k)
        if i+k in saw:	# not needed if sorted
            diff.add(i)
        saw.add(i)
    return len(diff)






def findPairs(self, nums: List[int], k: int) -> int:
    if k < 0:
        return 0
    if k == 0:
        return len(set([i for i in nums if nums.count(i)>=2]))
    cl = [i+k for i in nums]
    return len(set(cl)&set(nums))
















