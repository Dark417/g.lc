"""
158.645. Set Mismatch



The set S originally contains numbers from 1 to n. But unfortunately, due to the 
data error, one of the numbers in the set got duplicated to another number in the 
set, which results in repetition of one number and loss of another number.

Given an array nums representing the data status of this set after the error. 
Your task is to firstly find the number occurs twice and then find the number 
that is missing. Return them in the form of an array.

Example 1:
Input: nums = [1,2,2,4]
Output: [2,3]
Note:
The given array size will in the range [2, 10000].
The given array's numbers won't have any order.


"""

# consider all cases??

# def findErrorNums(self, nums: List[int]) -> List[int]:
#     nums.sort()
#     if nums[0] != 1:
#         return [nums[0], 1]
#     for i in range(1, len(nums)):
#         if nums[i] - nums[i-1] != 1:
#             return [nums[i], nums[i-1] + 1]



return [sum(nums) - sum(set(nums)), sum(range(1, len(nums)+1)) - sum(set(nums))]




def findErrorNums(self, A):
    N = len(A)
    count = [0] * (N+1)
    for x in A:
        count[x] += 1
    for x in range(1, len(A)+1):
        if count[x] == 2:
            twice = x
        if count[x] == 0:
            never = x
    return twice, never



def findErrorNums(self, nums):
    slots = [True] + [None] * len(nums)
    for n in nums:
        slots[n] = not slots[n]
    return slots.index(False), slots.index(None)



def findErrorNums(self, A):
    N = len(A)
    alpha = sum(A) - N*(N+1)/2
    beta = (sum(x*x for x in A) - N*(N+1)*(2*N+1)/6) / alpha
    return (alpha + beta) / 2, (beta - alpha) / 2



def findErrorNums(self, nums):
    x = sum(nums) - sum(set(nums))
    y = sum(range(len(nums)+1))-(sum(nums)-x)
    return [x,y]







def findErrorNums(self, nums: List[int]) -> List[int]:
	dup = missing = -1
	for i in range(1, len(nums)+1):
		cnt = 0
		for j in range(len(nums)):
			if nums[j] == i:
				cnt += 1
		if cnt == 2:
			dup = i
		elif cnt == 0:
			missing = i
	return [dup, missing]


def findErrorNums(self, nums: List[int]) -> List[int]:
	dup = missing = -1
	for i in range(1, len(nums)+1):
		cnt = 0
		for j in range(len(nums)):
			if nums[j] == i:
				cnt += 1
		if cnt == 2:
			dup = i
		elif cnt == 0:
			missing = i
		if dup>0 and missing >0:
			break
	return [dup, missing]


def findErrorNums(self, nums: List[int]) -> List[int]:
	nums.sort()
	dup = missing = 1
	for i in range(1, len(nums)):
		if nums[i] == nums[i-1]:
			dup = nums[i]
		elif nums[i] > nums[i-1]+1:
			missing = nums[i-1]+1
	return [dup, len(nums) if nums[-1] != len(nums) else missing]



def findErrorNums(self, nums: List[int]) -> List[int]:
	dic = {}
	dup = -1
	missing = 1
	for i in nums:
		if i not in dic:
			dic[i] = 0
		dic[i] += 1
		#dic[n] = dic.setdefault(i, 0) + 1
	for i in range(1, len(nums)+1):
		if i in dic:
			if dic[i] == 2
				dup = i
		else:
			missing = i
	return [dup, missing]



def findErrorNums(self, nums: List[int]) -> List[int]:
	arr = [0] * len(nums)+1
	dup = -1
	missing = 1
	for i in range(len(nums)):
		arr[nums[i]] += 1
	for i in range(1, len(nums)+1):
		if arr[i] == 0:
			missing = i
		elif arr[i] == 2:
			dup = i
	return [dup, missing]




































































