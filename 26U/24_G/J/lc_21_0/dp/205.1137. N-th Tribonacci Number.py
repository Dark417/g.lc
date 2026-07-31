"""
205.1137. N-th Tribonacci Number


The Tribonacci sequence Tn is defined as follows: 

T0 = 0, T1 = 1, T2 = 1, and Tn+3 = Tn + Tn+1 + Tn+2 for n >= 0.

Given n, return the value of Tn.

 

Example 1:

Input: n = 4
Output: 4
Explanation:
T_3 = 0 + 1 + 1 = 2
T_4 = 1 + 1 + 2 = 4
Example 2:

Input: n = 25
Output: 1389537
 

Constraints:

0 <= n <= 37
The answer is guaranteed to fit within a 32-bit integer, ie. answer <= 2^31 - 1.
"""

def tribonacci(self, n):
    a, b, c = 1, 0, 0
    for _ in xrange(n): a, b, c = b, c, a + b + c
    return c


def tribonacci(self, n: int) -> int:
        if n < 3:
            return 1 if n else 0
        
        x, y, z = 0, 1, 1
        for _ in range(n - 2):
            x, y, z = y, z, x + y + z
        return z


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



