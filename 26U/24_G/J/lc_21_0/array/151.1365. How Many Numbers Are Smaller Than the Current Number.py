"""
151.1365. How Many Numbers Are Smaller Than the Current Number

Given the array nums, for each nums[i] find out how many numbers in the array are smaller 
than it. That is, for each nums[i] you have to count the number of valid j's such that j != i and nums[j] < nums[i].

Return the answer in an array.

 

Example 1:

Input: nums = [8,1,2,2,3]
Output: [4,0,1,1,3]
Explanation: 
For nums[0]=8 there exist four smaller numbers than it (1, 2, 2 and 3). 
For nums[1]=1 does not exist any smaller number than it.
For nums[2]=2 there exist one smaller number than it (1). 
For nums[3]=2 there exist one smaller number than it (1). 
For nums[4]=3 there exist three smaller numbers than it (1, 2 and 2).
Example 2:

Input: nums = [6,5,4,8]
Output: [2,1,0,3]
Example 3:

Input: nums = [7,7,7,7]
Output: [0,0,0,0]
 

Constraints:

2 <= nums.length <= 500
0 <= nums[i] <= 100
"""

def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
    return [sum(x < i for x in nums ) for i in nums]


return [sorted(nums).index(a) for a in nums]

sorted_nums = sorted(nums)
return [sorted_nums.index(num) for num in nums]



def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
    indices = {}
    for idx, num in enumerate(sorted(nums)):
        indices.setdefault(num, idx)
    return [indices[num] for num in nums]



def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
    n = len(nums)
    cnt, vec = [0] * 101, [0] * n
    for num in nums:
        cnt[num] += 1
    for i in range(1, 101):
        cnt[i] += cnt[i - 1]
    for i in range(n):
        if nums[i]:
            vec[i] = cnt[nums[i] - 1]
    return vec




def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
    count = [0] * 102
    for num in nums:
        count[num+1] += 1
    for i in range(1, 102):
        count[i] += count[i-1]
    return [count[num] for num in nums]




def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
    n = len(nums)
    vec = [0] * n
    tmp = sorted([(nums[i], i) for i in range(n)])
    
    pre = -1
    for i in range(n):
        if i != 0 and tmp[i][0] != tmp[i - 1][0]:
            pre = i - 1
        vec[tmp[i][1]] = pre + 1
    return vec





# bucket
def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
    buckets = [0] * 101
    
    for num in nums:
        buckets[num] += 1
        
    previous = 0    
    for i, bucket in enumerate(buckets):
        if bucket != 0:
            buckets[i] = previous 
            previous += bucket 
            
    return [buckets[num] for num in nums]















































