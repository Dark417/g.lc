"""
223.628. Maximum Product of Three Numbers
三个数的最大乘积


Given an integer array, find three numbers whose product is maximum and output the maximum product.

Example 1:

Input: [1,2,3]
Output: 6
 

Example 2:

Input: [1,2,3,4]
Output: 24


Note:

The length of the given array will be in range [3,104] and all elements are in the range [-1000, 1000].
Multiplication of any three numbers in the input won't exceed the range of 32-bit signed integer.

"""

def maximumProduct(self, A):
    A.sort()
    del A[3:-3]
    return max(a * b * c for a, b, c in itertools.combinations(A, 3))


def maximumProduct(self, nums: List[int]) -> int:
    nums.sort()
    return max(nums[0]*nums[1]*nums[-1], nums[-3]*nums[-2]*nums[-1])



def maximumProduct(self, nums):
    a, b = heapq.nlargest(3, nums), heapq.nsmallest(2, nums)
    return max(a[0] * a[1] * a[2], b[0] * b[1] * a[0])


return max(nums) * max(a * b for a, b in [heapq.nsmallest(2, nums), heapq.nlargest(3, nums)[1:]])



def maximumProduct(self, nums):
    import heapq
    from operator import mul
    from functools import reduce
    three_max = heapq.nlargest(3, nums)
    two_min = heapq.nsmallest(2, nums)
    return max(reduce(mul, three_max), reduce(mul, two_min + three_max[:1]))


import functools
import itertools
from operator import mul
class Solution:
    def maximumProduct(self, nums):
        nums = sorted(nums)
        del nums[3:-3]
        return max(functools.reduce(mul, c) for c in itertools.combinations(nums, 3))




def maximumProduct(self, nums: List[int]) -> int:
    min1 = min2 = float("inf")
    max1 = max2 = max3 = -min1
    for n in nums:
        if n < min1:
            min2 = min1
            min1 = n
        elif n < min2:
            min2 = n
        if n > max1:
            max3 = max2
            max2 = max1
            max1 = n
        elif n > max2:
            max3 = max2
            max2 = n
        elif n > max3:
            max3 = n
    return max(min1*min2*max1, max1* max2* max3)

















































