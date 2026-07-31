# 1413. 逐步求和得到正数的最小值

def minStartValue(self, nums: List[int]) -> int:
    n = len(nums)
    presum = [0] * n
    for i in range(len(nums)):
        presum[i] = nums[i] if i == 0 else presum[i - 1] + nums[i]
    m = min(presum)
    return 1 if m > 0 else -m + 1

