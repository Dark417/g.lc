# 303. 区域和检索 - 数组不可变

class NumArray:

    def __init__(self, nums: List[int]):
        n = len(nums)
        self.l = [0] * (n+1)
        for i in range(n):
            self.l[i+1] = self.l[i] + nums[i]

    def sumRange(self, i: int, j: int) -> int:
        return self.l[j+1] - self.l[i]



class NumArray:

    def __init__(self, nums: List[int]):
        self.nums = nums

    def sumRange(self, i: int, j: int) -> int:
        l = [0]
        for k in self.nums:
            l.append(l[-1] + k)
        return l[j+1] - l[i]



class NumArray:

    def __init__(self, nums: List[int]):
        self.nums = nums

    def sumRange(self, i: int, j: int) -> int:
        return sum(k for k in self.nums[i:j+1])




