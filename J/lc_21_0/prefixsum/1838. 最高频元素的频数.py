# 1838. 最高频元素的频数


def maxFrequency(self, nums: List[int], k: int) -> int:
    nums.sort()
    n = len(nums)
    l = 0
    total = 0
    res = 1
    for r in range(1, n):
        total += (nums[r] - nums[r - 1]) * (r - l)
        while total > k:
            total -= nums[r] - nums[l]
            l += 1
        res = max(res, r - l + 1)
    return res



def maxFrequency(self, nums: List[int], k: int) -> int:
    n = len(nums)
    #---------- 贪心，先排序
    nums.sort()
    #---------- 前缀和，为了方便求区间和
    presum = [0 for _ in range(n + 1)]
    for i in range(1, n + 1):
        presum[i] = presum[i-1] + nums[i-1]
    
    res = 1
    for i in range(1, n + 1):
        L = 1
        R = i
        #---------- 二分查找，寻找符合条件的最左端
        while L < R:
            mid = L + R >> 1
            if nums[i-1] * (i - mid + 1) - (presum[i] - presum[mid - 1]) <= k:
                R = mid
            else:
                L = mid + 1
        res = max(res, i - L + 1)

    return res




