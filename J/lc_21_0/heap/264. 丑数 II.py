# 313. 超级丑数

def nthSuperUglyNumber(self, n: int, primes: List[int]) -> int:
    nums = [1] * n
    pi = [0] * len(primes)
    
    for i in range(1, n):
        nums[i] = min(nums[pi[p]] * primes[p] for p in range(len(primes)))
        for p in range(len(primes)):
            if nums[i] == nums[pi[p]] * primes[p]:
                pi[p] += 1
    return nums[-1]


# 264. 丑数 II



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



def nthUglyNumber(self, n: int) -> int:
    res=[1]
    index=[0,0,0]
    number=[2,3,5]
    for i in range(n):
        tmp = [res[index[j]]*number[j] for j in range(3)]
        res.append(min(tmp))
        for j in range(3):
            if tmp[j] == res[-1]:
                index[j]+=1;
    return res[n-1];


def nthUglyNumber(self, n: int) -> int:
    seen = {1}
    # nums = []
    hp = [1]
    heapq.heapify(hp)
    for _ in range(n):
        cur = heapq.heappop(hp)
        # nums.append(cur)
        for i in [2, 3, 5]:
            new = cur * i
            if new not in seen:
                seen.add(new)
                heapq.heappush(hp, new)
        
    return cur

# from heapq import heappop, heappush
# class Ugly:
#     def __init__(self):
#         seen = {1, }
#         self.nums = nums = []
#         heap = []
#         heappush(heap, 1)

#         for _ in range(1690):
#             curr_ugly = heappop(heap)
#             nums.append(curr_ugly)
#             for i in [2, 3, 5]:
#                 new_ugly = curr_ugly * i
#                 if new_ugly not in seen:
#                     seen.add(new_ugly)
#                     heappush(heap, new_ugly)
    
# class Solution:
#     u = Ugly()
#     def nthUglyNumber(self, n):
#         return self.u.nums[n - 1]


def nthUglyNumber(self, n: int) -> int:
    nums = [1]
    i2 = i3 = i5 = 0
    
    for i in range(n-1):
        ugly = min(nums[i2]*2, nums[i3]*3, nums[i5]*5)
        nums.append(ugly)
        
        if ugly == nums[i2] * 2:
            i2 += 1
        if ugly == nums[i3] * 3:
            i3 += 1
        if ugly == nums[i5] * 5:
            i5 += 1
        
    return nums[-1]


# class Ugly:
#     def __init__(self):
#         self.nums = nums = [1, ]
#         i2 = i3 = i5 = 0

#         for i in range(1, 1690):
#             ugly = min(nums[i2] * 2, nums[i3] * 3, nums[i5] * 5)
#             nums.append(ugly)

#             if ugly == nums[i2] * 2: 
#                 i2 += 1
#             if ugly == nums[i3] * 3:
#                 i3 += 1
#             if ugly == nums[i5] * 5:
#                 i5 += 1

# class Solution:
#     u = Ugly()
#     def nthUglyNumber(self, n):
#         return self.u.nums[n - 1]






# 263. 丑数

def isUgly(self, num: int) -> bool:
    for p in 2, 3, 5:
        while num % p == 0 < num:
            num /= p
    return num == 1




def isUgly(self, num: int) -> bool:
    if num < 1: return False
    if num == 1: return True
    if num % 2 == 0:
        return self.isUgly(num / 2) 
    elif num % 3 == 0:
        return self.isUgly(num / 3) 
    elif num % 5 == 0:
        return self.isUgly(num / 5) 
    else:
        return False



def isUgly(self, num: int) -> bool:
    if num <1: return False
    while num != 1:
        if num // 2 == num / 2:
            num //= 2
        elif num // 3 == num / 3:
            num //= 3
        elif num // 5 == num / 5:
            num //= 5
        else:
            return False
    return True





































