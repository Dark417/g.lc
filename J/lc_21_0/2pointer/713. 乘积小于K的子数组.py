# 713. 乘积小于K的子数组


def numSubarrayProductLessThanK(self, nums, k):
    if k <= 1: return 0
    prod = 1
    ans = left = 0
    for right, val in enumerate(nums):
        prod *= val
        while prod >= k:
            prod /= nums[left]
            left += 1
        ans += right - left + 1
    return ans



def numSubarrayProductLessThanK(self, nums, k):
    if k == 0: return 0
    k = math.log(k)

    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + math.log(x))

    ans = 0
    for i, x in enumerate(prefix):
        j = bisect.bisect(prefix, x + k - 1e-9, i+1)
        ans += j - i - 1
    return ans



