# 1004. 最大连续1的个数 III

# bs
def longestOnes(self, nums: List[int], k: int) -> int:
    n = len(nums)
    P = [0]
    for num in nums:
        P.append(P[-1] + (1 - num))
    
    ans = 0
    for right in range(n):
        left = bisect.bisect_left(P, P[right + 1] - k)
        ans = max(ans, right - left + 1)
    
    return ans


# sw
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


def longestOnes(self, nums: List[int], k: int) -> int:
    n = len(nums)
    left = lsum = rsum = 0
    ans = 0
    
    for right in range(n):
        rsum += 1 - nums[right]
        while lsum < rsum - k:
            lsum += 1 - nums[left]
            left += 1
        ans = max(ans, right - left + 1)
    
    return ans



























