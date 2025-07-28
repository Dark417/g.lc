# 1856. 子数组最小乘积的最大值

def maxSumMinProduct(self, nums: List[int]) -> int:
    mod = 10**9 + 7

    n = len(nums)
    # 数组 left 初始化为 0，数组 right 初始化为 n-1
    # 设置为元素不存在时的特殊值
    left, right = [0] * n, [n - 1] * n
    # 单调栈
    s = list()
    for i, num in enumerate(nums):
        while s and nums[s[-1]] >= num:
            # 这里的 right 是非严格定义的，right[i] 是右侧最近的小于等于 nums[i] 的元素下标
            right[s[-1]] = i - 1
            s.pop()
        if s:
            # 这里的 left 是严格定义的，left[i] 是左侧最近的严格小于 nums[i] 的元素下标
            left[i] = s[-1] + 1
        s.append(i)
    
    # 前缀和
    pre = [0]
    for i, num in enumerate(nums):
        pre.append(pre[-1] + num)
    
    best = max((pre[right[i] + 1] - pre[left[i]]) * num for i, num in enumerate(nums))
    return best % mod

































