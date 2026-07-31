"""
187.198. House Robber
打家劫舍


You are a professional robber planning to rob houses along a street. Each house has a certain 
amount of money stashed, the only constraint stopping you from robbing each of them 
is that adjacent houses have security system connected and it will automatically contact 
the police if two adjacent houses were broken into on the same night.

Given a list of non-negative integers representing the amount of money of each house, 
determine the maximum amount of money you can rob tonight without alerting the police.

 

Example 1:

Input: nums = [1,2,3,1]
Output: 4
Explanation: Rob house 1 (money = 1) and then rob house 3 (money = 3).
             Total amount you can rob = 1 + 3 = 4.
Example 2:

Input: nums = [2,7,9,3,1]
Output: 12
Explanation: Rob house 1 (money = 2), rob house 3 (money = 9) and rob house 5 (money = 1).
             Total amount you can rob = 2 + 9 + 1 = 12.
 

Constraints:

0 <= nums.length <= 100
0 <= nums[i] <= 400

https://leetcode-cn.com/problems/the-masseuse-lcci/solution/an-mo-shi-by-leetcode-solution/

From good to great. How to approach most of DP problems.
https://leetcode.com/problems/house-robber/discuss/156523/From-good-to-great.-How-to-approach-most-of-DP-problems.
"""



f(0) = nums[0]
f(1) = max(num[0], num[1])
f(k) = max( f(k-2) + nums[k], f(k-1) )

def rob(self, nums):
        last, now = 0, 0
        for i in nums: last, now = now, max(last + i, now)  
        return now


# *nice
def rob(self, num):
	i, e = 0, 0
    for n in num: # from k-1 to k
        i, e = n+e, max(i,e)
    return max(i,e)



def rob(self, nums):
    l = r = 0
    for n in nums:
        l, r = r, max(n + l, r)
    return r



def rob(self, nums):
	Rob = non_Rob = 0
	for n in nums:
		non_Rob, Rob = max(non_Rob, Rob), non_Rob + n
	return max(Rob, non_Rob)



# D
# extra space
def rob(self, nums: List[int]) -> int:
    if not nums: return 0
    dp = [0] * len(nums)
    dp[0] = nums[0]
    for i in range(1, len(nums)):
        dp[i] = max(dp[i-2] + nums[i], dp[i-1])
    return dp[-1]


def rob(self, nums: List[int]) -> int:
    if len(nums) == 0:
        return 0
    # 子问题：
    # f(k) = 偷 [0..k) 房间中的最大金额

    # f(0) = 0
    # f(1) = nums[0]
    # f(k) = max{ rob(k-1), nums[k-1] + rob(k-2) }
	N = len(nums)
    dp = [0] * (N+1)
    dp[0] = 0
    dp[1] = nums[0]
    for k in range(2, N+1):
        dp[k] = max(dp[k-1], nums[k-1] + dp[k-2])
    return dp[N]





# dynamic vars
def rob(self, nums: List[int]) -> int:
    prev = 0
    curr = 0
    # 每次循环，计算“偷到当前房子为止的最大金额”
    for i in nums:
        # 循环开始时，curr 表示 dp[k-1]，prev 表示 dp[k-2]
        # dp[k] = max{ dp[k-1], dp[k-2] + i }
        prev, curr = curr, max(curr, prev + i)
        # 循环结束时，curr 表示 dp[k]，prev 表示 dp[k-1]

    return curr




def rob(self, nums: List[int]) -> int:
    if not nums: return 0
    if len(nums) == 1: return nums[0]
    if len(nums) == 2: return max(nums)
    f = nums[0]
    s = max(nums[0], nums[1])
    for i in range(2, len(nums)):
        cur = max(f + nums[i], s)
        f, s = s, cur
    return cur


def rob(self, nums: List[int]) -> int:
    if not nums: return 0
    f, s = 0, nums[0]
    cur = nums[0]
    for i in range(1, len(nums)):
        cur = max(f + nums[i], s)
        f, s = s, cur
    return max(cur, f)


# official
def rob(self, nums: List[int]) -> int:
    if not nums:
        return 0
    size = len(nums)
    if size == 1:
        return nums[0]
    dp = [0] * size
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])
    for i in range(2, size):
        dp[i] = max(dp[i - 2] + nums[i], dp[i - 1])
    return dp[size - 1]








def rob(self, num):
    max_3_house_before, max_2_house_before, adjacent = 0, 0, 0
    for cur in num:
        max_3_house_before, max_2_house_before, adjacent = \
        max_2_house_before, adjacent, max(max_3_house_before+cur, max_2_house_before+cur)
    return max(max_2_house_before, adjacent)







































