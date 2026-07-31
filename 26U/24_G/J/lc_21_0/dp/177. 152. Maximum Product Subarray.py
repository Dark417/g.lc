"""
177. 152. Maximum Product Subarray
乘积最大子数组

Given an integer array nums, find the contiguous subarray within an array (containing 
at least one number) which has the largest product.

Example 1:

Input: [2,3,-2,4]
Output: 6
Explanation: [2,3] has the largest product 6.
Example 2:

Input: [-2,0,-1]
Output: 0
Explanation: The result cannot be 2, because [-2,-1] is not a subarray.

"""

from operator import mul
reduce(mul, list, 1)



"""
def maxProduct(self, nums: List[int]) -> int:
    if not nums: return None
    mpdt = nums[0]
    if len(nums) == 1: return mpdt
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            mpdt = max(mpdt, reduce((lambda x, y: x * y), nums[i:j+1]))
    return mpdt
"""


def maxProduct(self, nums: List[int]) -> int:
    if len(nums) == 0:
        return 0
    result = nums[0]
    for i in range(len(nums)):
        accu = 1
        for j in range(i, len(nums)):
            accu *= nums[j]
            result = max(result, accu)

    return result



def maxProduct(self, nums: List[int]) -> int:
    if not nums: return 
    res = nums[0]
    pre_max = nums[0]
    pre_min = nums[0]
    for num in nums[1:]:
        cur_max = max(pre_max * num, pre_min * num, num)
        cur_min = min(pre_max * num, pre_min * num, num)
        res = max(res, cur_max)
        pre_max = cur_max
        pre_min = cur_min
    return res



def maxProduct(self, nums):
    max_prod, min_prod, ans = nums[0], nums[0], nums[0]
    for i in range(1, len(nums)):
        x = max(nums[i], max_prod*nums[i], min_prod*nums[i])
        y = min(nums[i], max_prod*nums[i], min_prod*nums[i])            
        max_prod, min_prod = x, y
        ans = max(max_prod, ans)
    return ans


def maxProduct(nums):
    maximum=big=small=nums[0]
    for n in nums[1:]:
        big, small=max(n, n*big, n*small), min(n, n*big, n*small)
        maximum=max(maximum, big)
    return maximum

    

def maxProduct(self, nums: List[int]) -> int:
    reverse_nums = nums[::-1]
    for i in range(1, len(nums)):
        nums[i] *= nums[i - 1] or 1
        reverse_nums[i] *= reverse_nums[i - 1] or 1
    return max(nums + reverse_nums)



# lee
def maxProduct(self, A):
    B = A[::-1]
    for i in range(1, len(A)):
        A[i] *= A[i - 1] or 1
        B[i] *= B[i - 1] or 1
    return max(A + B)







def maxProduct(self, A):
    res = small = big = A[0]
    for i in A[1:]:
        small, _, big = sorted([small * i, big * i, i])
        res = max(res, small, big)
    return res





# https://leetcode-cn.com/problems/maximum-product-subarray/solution/duo-chong-si-lu-qiu-jie-by-powcai-3/

def maxProduct(self, nums: List[int]) -> int:
    if not nums: return
    # 目前的累乘
    cur_pro = 1
    # 前面最小的正数
    min_pos = 1
    # 前面最大的负数
    max_neg = float("-inf")
    # 结果
    res = float("-inf")
    for num in nums:
        cur_pro *= num
        # 考虑三种情况
        # 大于0
        if cur_pro > 0:
            res = max(res, cur_pro // min_pos)
            min_pos = min(min_pos, cur_pro)
        # 小于0
        elif cur_pro < 0:
            if max_neg != float("-inf"):
                res = max(res, cur_pro // max_neg)
            else:
                res = max(res, num)
            max_neg = max(max_neg, cur_pro)
        # 等于0 
        else:
            cur_pro = 1
            min_pos = 1
            max_neg = float("-inf")
            res = max(res, num)
    return res 





def maxProduct(self, nums: List[int]) -> int:
    prefix, suffix, res = 0, 0, -float('inf')
    for i in range(len(nums)):
        prefix = nums[i] if not prefix else nums[i]*prefix
        suffix = nums[-i - 1] if not suffix else nums[-i - 1]*suffix
        res = max(res, prefix, suffix)
    return res




# panda
def maxProduct(self, nums: List[int]) -> int:
    if len(nums) == 0: return 0
    if len(nums) == 1: return nums[0]
    res = nums[0]  # 结果变量初始化
    # dp[i][0]存储到当前层可达到最大
    # dp[i][1]存储到当前层可达到最小
    dp = [[0] * 2 for _ in range(len(nums))]
    dp[0][0], dp[0][1] = nums[0], nums[0]
    for i in range(1, len(nums)):
        left = nums[i] * dp[i - 1][0]
        right = nums[i] * dp[i - 1][1]
        # 因为当前nums[i]可正可负，所以得到的left，right大小关系不确定
        dp[i][0] = max(left, right, nums[i])
        dp[i][1] = min(left, right, nums[i])
        res = max(res, dp[i][0])
    return res


def maxProduct(self, nums: List[int]) -> int:
    if len(nums) == 0: return 0
    if len(nums) == 1: return nums[0]
    res = nums[0]  # 结果变量初始化
    pre_max, pre_min = nums[0], nums[0]
    for i in range(1, len(nums)):
        left = nums[i] * pre_max
        right = nums[i] * pre_min
        # 因为当前nums[i]可正可负，所以得到的left，right大小关系不确定
        pre_max = max(left, right, nums[i])
        pre_min = min(left, right, nums[i])
        res = max(res, pre_max)
    return res


def maxProduct(self, nums: List[int]) -> int:
    maxval = float('-inf')
    imax, imin = 1, 1
    for i in range(len(nums)):
        if nums[i] < 0:
            imax, imin = imin, imax
        imax = max(imax * nums[i], nums[i])
        imin = min(imin * nums[i], nums[i])
        maxval = max(maxval, imax)
    return maxval

































































