# 136. 只出现一次的数字

def singleNumber(self, nums: List[int]) -> int:
    return reduce(lambda x, y: x ^ y, nums)

























