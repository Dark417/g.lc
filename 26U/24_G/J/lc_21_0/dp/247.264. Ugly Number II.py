"""
247.264. Ugly Number II
丑数 II

Write a program to find the n-th ugly number.

Ugly numbers are positive numbers whose prime factors only include 2, 3, 5. 

Example:

Input: n = 10
Output: 12
Explanation: 1, 2, 3, 4, 5, 6, 8, 9, 10, 12 is the sequence of the first 10 ugly numbers.
Note:  

1 is typically treated as an ugly number.
n does not exceed 1690.


"""



# Stefan
ugly = sorted(2**a * 3**b * 5**c
                  for a in range(32) for b in range(20) for c in range(14))
def nthUglyNumber(self, n):
    return self.ugly[n-1]



def nthUglyNumber(self, n):
    ugly = [1]
    i2 = i3 = i5 = 0
    while len(ugly) < n:
        while ugly[i2] * 2 <= ugly[-1]: i2 += 1
        while ugly[i3] * 3 <= ugly[-1]: i3 += 1
        while ugly[i5] * 5 <= ugly[-1]: i5 += 1
        ugly.append(min(ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5))
    return ugly[-1]





def nthUglyNumber(self, n):
    q2, q3, q5 = [2], [3], [5]
    ugly = 1
    for u in heapq.merge(q2, q3, q5):
        if n == 1:
            return ugly
        if u > ugly:
            ugly = u
            n -= 1
            q2 += 2 * u,
            q3 += 3 * u,
            q5 += 5 * u,




def nthUglyNumber(self, n):
    factor = 2, 3, 5
    lists = [collections.deque([1]) for _ in range(3)]
    for _ in range(n - 1):
        next = [lists[i][0] * factor[i] for i in range(3)]
        winner = min(range(3), key=lambda j: next[j])
        for i in range(winner, 3):
            lists[i] += next[winner],
        lists[winner].popleft()
    return lists[2][-1]



def nthUglyNumber(self, n: int) -> int:
    factors, k = [2,3,5], 3
    starts, Numbers = [0] * k, [1]
    for i in range(n-1):
        candidates = [factors[i]*Numbers[starts[i]] for i in range(k)]
        new_num = min(candidates)
        Numbers.append(new_num)
        starts = [starts[i] + (candidates[i] == new_num) for i in range(k)]
    return Numbers[-1]



def nthUglyNumber(self, n: int) -> int:
    dp = [0] * n
    dp[0] = 1
    l2, l3, l5 = 0, 0, 0
    for i in range(1, n):
        dp[i] = min(2 * dp[l2], 3 * dp[l3], 5 * dp[l5])
        if dp[i] == 2 * dp[l2]:
            l2 += 1
        if dp[i] == 3 * dp[l3]:
            l3 += 1
        if dp[i] == 5 * dp[l5]:
            l5 += 1
    return dp[n - 1]





class Ugly:
    def __init__(self):
        self.nums = nums = [1, ]
        i2 = i3 = i5 = 0

        for i in range(1, 1690):
            ugly = min(nums[i2] * 2, nums[i3] * 3, nums[i5] * 5)
            nums.append(ugly)

            if ugly == nums[i2] * 2: 
                i2 += 1
            if ugly == nums[i3] * 3:
                i3 += 1
            if ugly == nums[i5] * 5:
                i5 += 1
            
class Solution:
    u = Ugly()
    def nthUglyNumber(self, n):
        return self.u.nums[n - 1]







from heapq import heappop, heappush
class Ugly:
    def __init__(self):
        seen = {1, }
        self.nums = nums = []
        heap = []
        heappush(heap, 1)

        for _ in range(1690):
            curr_ugly = heappop(heap)
            nums.append(curr_ugly)
            for i in [2, 3, 5]:
                new_ugly = curr_ugly * i
                if new_ugly not in seen:
                    seen.add(new_ugly)
                    heappush(heap, new_ugly)
    
class Solution:
    u = Ugly()
    def nthUglyNumber(self, n):
        return self.u.nums[n - 1]



























































































