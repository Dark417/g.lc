# 剑指 Offer 42. 连续子数组的最大和


def maxSubArray(self, nums: List[int]) -> int:
    for i in range(1, len(nums)):
        if nums[i-1] > 0:
            nums[i] = nums[i-1] + nums[i] 
    return max(nums)


def maxSubArray(self, nums: List[int]) -> int:
    for i in range(1, len(nums)):
        nums[i] += max(nums[i - 1], 0)
    return max(nums)



# brtue force
# 

















