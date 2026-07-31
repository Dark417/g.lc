"""
207.303. Range Sum Query - Immutable
区域和检索 - 数组不可变

Given an integer array nums, find the sum of the elements between indices i and j (i ≤ j), inclusive.

Example:
Given nums = [-2, 0, 3, -5, 2, -1]

sumRange(0, 2) -> 1
sumRange(2, 5) -> -1
sumRange(0, 5) -> -3
Note:
You may assume that the array does not change.
There are many calls to sumRange function.

"""



def __init__(self, nums: List[int]):
    self.nums = nums
    self.l = [0]
    for k in self.nums:
        self.l.append(self.l[-1] + k)

    self.arr={-1:0}
    for i in range(len(nums)):
        self.arr[i]=self.arr[i-1]+nums[i]


    self.lists = [0]
    # error out of range when use nums[0] here
    # nums[0]
    for i, n in enumerate(nums):
        # No O(N) cause
        if i == 0:
            self.lists.append(nums[i])
        else:
            self.lists.append(self.lists[i] + n)



def sumRange(self, i: int, j: int) -> int:
    return self.l[j+1] - self.l[i]




def __init__(self, nums):
    self.dp = nums

    for i in xrange(1, len(nums)):
        self.dp[i] += self.dp[i-1]

def sumRange(self, i, j):
    return self.dp[j] - (self.dp[i-1] if i > 0 else 0)


def __init__(self, nums):
    self.dp = [0]+nums[:]
    for i in xrange(1, len(nums)+1):
        self.dp[i] += self.dp[i-1]

def sumRange(self, i, j):
    return self.dp[j+1]-self.dp[i]




def sumRange(self, i: int, j: int) -> int:
    return sum(k for k in self.nums[i:j+1])












































































