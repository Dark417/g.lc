# 1137. 第 N 个泰波那契数

def tribonacci(self, n: int) -> int:
        a, b, c = 0, 0, 1
    for i in range(n):
        a, b, c = b, c, a+b+c
    return b


class Tri:
    def __init__(self):
        def helper(k):
            if k == 0:
                return 0
            
            if nums[k]:
                return nums[k]

            nums[k] = helper(k - 1) + helper(k - 2) + helper(k - 3) 
            return nums[k]
        
        n = 38
        self.nums = nums = [0] * n
        nums[1] = nums[2] = 1
        helper(n - 1)
                    
class Solution:
    t = Tri()
    def tribonacci(self, n: int) -> int:
        return self.t.nums[n]


class Tri:
    def __init__(self):
        n = 38
        self.nums = nums = [0] * n
        nums[1] = nums[2] = 1
        for i in range(3, n):
            nums[i] = nums[i - 1] + nums[i - 2] + nums[i - 3]
                    
class Solution:
    t = Tri()
    def tribonacci(self, n: int) -> int:
        return self.t.nums[n]


































