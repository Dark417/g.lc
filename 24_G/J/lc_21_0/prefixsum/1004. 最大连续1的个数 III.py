# 1004. 最大连续1的个数 III


def longestOnes(self, nums: List[int], K: int) -> int:
    l = res = zero = 0
    for r in range(len(nums)):
        if nums[r] == 0:
            zero += 1
        while zero > K:
            if nums[l] == 0:
                zero -= 1
            l += 1
        res = max(res, r - l + 1)
    return res



























