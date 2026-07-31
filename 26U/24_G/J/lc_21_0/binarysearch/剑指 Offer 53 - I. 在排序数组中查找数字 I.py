# 剑指 Offer 53 - I. 在排序数组中查找数字 I

"""
[5,7,7,8,8,10]
8
"""

def search(self, nums: [int], target: int) -> int:
    def helper(tar):
        i, j = 0, len(nums) - 1
        while i <= j:
            m = (i + j) // 2
            if nums[m] <= tar: i = m + 1
            else: j = m - 1
        return i   
    return helper(target) - helper(target - 1)

# 如果nums[m] <= tar, i = m + 1, 最终i为target+1


def search(self, nums: List[int], target: int) -> int:
        
    n = len(nums)
    if n == 0:
        return 0
    
    l, r = 0, n - 1
    while l <= r:
        mid = (l + r) // 2
        if nums[mid] >= target:
            r = mid - 1
        else:
            l = mid + 1
    if l ==n or nums[l] != target:
        return 0
    else:
        k = 1
        for i in range(l + 1, n):
            if nums[i] == target:
                k += 1
        return k









































