"""
145.1512. Number of Good Pairs
好数对的数目

Given an array of integers nums.

A pair (i,j) is called good if nums[i] == nums[j] and i < j.

Return the number of good pairs.

 

Example 1:

Input: nums = [1,2,3,1,1,3]
Output: 4
Explanation: There are 4 good pairs (0,3), (0,4), (3,4), (2,5) 0-indexed.
Example 2:

Input: nums = [1,1,1,1]
Output: 6
Explanation: Each pair in the array are good.
Example 3:

Input: nums = [1,2,3]
Output: 0
 

Constraints:

1 <= nums.length <= 100
1 <= nums[i] <= 100
"""


from collections import Counter
    nm = Counter(nums)
    res = 0
    def fac(n):
        i = 1
        pdt = 1
        while i<=n:
            pdt *= i
            i += 1
        return pdt

    for val in nm.values():
        if val >= 2:
            res += fac(val) // fac(2) // fac(val-2)
    return res



return sum([nums[inx+1:].count(i) for inx, i in enumerate(nums)])
return sum(nums[idx+1:].count(nums[idx]) for idx in range(len(nums)-1))

return sum(k * (k - 1) / 2 for k in collections.Counter(A).values())


# brute force
# double loop
return sum(1 if nums[i] == nums[j] for j in range(i+1,len(nums) for i in range(len(nums)-1)))
def numIdenticalPairs(self, nums: List[int]) -> int:
	res = 0
	for i in range(len(nums)-1):
		for j in range(i+1, len(nums)):
			if nums[i] == nums[j]: res += 1
	return res


def numIdenticalPairs(self, nums: List[int]) -> int:
    ret, dct = 0, defaultdict(int)
    for i in nums:
        ret, dct[i] = ret+dct[i], dct[i]+1
    return ret













































