# 523. 连续的子数组和


def checkSubarraySum(self, nums: List[int], k: int) -> bool:
    modes = set()
    presum = 0
    for num in nums:
        last = presum
        # 当前前缀和
        presum += num
        presum %= k
        # 同余定理
        if presum in modes:
            return True
        # 上一个前缀和，下一个就可以用了（距离为2了）
        modes.add(last)
    return False




























