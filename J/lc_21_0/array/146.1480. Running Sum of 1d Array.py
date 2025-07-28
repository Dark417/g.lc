"""
146.1480. Running Sum of 1d Array
一维数组的动态和

Given an array nums. We define a running sum of an array as runningSum[i] = sum(nums[0]…nums[i]).

Return the running sum of nums.

 

Example 1:

Input: nums = [1,2,3,4]
Output: [1,3,6,10]
Explanation: Running sum is obtained as follows: [1, 1+2, 1+2+3, 1+2+3+4].
Example 2:

Input: nums = [1,1,1,1,1]
Output: [1,2,3,4,5]
Explanation: Running sum is obtained as follows: [1, 1+1, 1+1+1, 1+1+1+1, 1+1+1+1+1].
Example 3:

Input: nums = [3,1,2,10,1]
Output: [3,4,6,16,17]
 

Constraints:

1 <= nums.length <= 1000
-10^6 <= nums[i] <= 10^6


"""

return itertools.accumulate(nums)
return list(itertools.accumulate(A))

return [*itertools.accumulate(nums)]



return [sum(nums[:i+1]) for i in range(len(nums))]


def runningSum(self, nums: List[int]) -> List[int]:
    s = 0
    l = []
    for i in range(len(nums)):
        l.append(s+nums[i])
        s += nums[i]
    return l


def runningSum(self, nums: List[int]) -> List[int]:
    l = [nums[0]] * len(nums)
    for i in range(1,len(nums)):
        l[i] = l[i-1] + nums[i]

        l[i] = l[i-1] + nums[i] if i>0 else nums[0]
    return l








































