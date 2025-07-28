"""
199.213. House Robber II
打家劫舍

You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. All houses at this place are arranged in a circle. That means the first house is the neighbor of the last one. Meanwhile, adjacent houses have security system connected and it will automatically contact the police if two adjacent houses were broken into on the same night.

Given a list of non-negative integers representing the amount of money of each house, determine the maximum amount of money you can rob tonight without alerting the police.

Example 1:

Input: [2,3,2]
Output: 3
Explanation: You cannot rob house 1 (money = 2) and then rob house 3 (money = 2),
             because they are adjacent houses.
Example 2:

Input: [1,2,3,1]
Output: 4
Explanation: Rob house 1 (money = 1) and then rob house 3 (money = 3).
             Total amount you can rob = 1 + 3 = 4.

"""


def rob(self, nums):
    def rob(nums):
        now = prev = 0
        for n in nums:
            now, prev = max(now, prev + n), now
        return now
    return max(rob(nums[len(nums) != 1:]), rob(nums[:-1]))

        
#
def rob(self, nums: List[int]) -> int:
    def rec(l):
        a, b = 0, 0
        for i in l:
            a, b = b, max(a+i, b)
        return b
    return max(rec(nums[1:]), rec(nums[:-1])) if len(nums) != 1 else nums[0]



def rob(self, nums: [int]) -> int:
    def my_rob(nums):
        cur, pre = 0, 0
        for num in nums:
            cur, pre = max(pre + num, cur), cur
        return cur
    return max(my_rob(nums[:-1]),my_rob(nums[1:])) if len(nums) != 1 else nums[0]



def rob(self, nums: List[int]) -> int:
    if not nums or len(nums) == 1:
        return sum(nums)
    a, b, c, d = 0, 0, 0, nums[0]
    for i in nums[1: -1]:
        a, b, c, d = b, max(b, a+i), d, max(d, c+i)
    return max(b, a+nums[-1], d)
















































































