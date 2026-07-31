#heap

# 剑指 Offer 40. 最小的k个数


def getLeastNumbers(self, arr: List[int], k: int) -> List[int]:
    if k == 0:
        return list()

    hp = [-x for x in arr[:k]]
    heapq.heapify(hp)
    for i in range(k, len(arr)):
        if -hp[0] > arr[i]:
            heapq.heappop(hp)
            heapq.heappush(hp, -arr[i])
    ans = [-x for x in hp]
    return ans


def getLeastNumbers(self, arr: List[int], k: int) -> List[int]:
    heapq.heapify(arr)
    res = []
    for _ in range(k):
        res.append(heapq.heappop(arr))
    return res



# 1046. 最后一块石头的重量

def lastStoneWeight(self, stones: List[int]) -> int:
    s = [-i for i in stones]
    heapq.heapify(s)
    
    while len(s) >= 2:
        x1 = heapq.heappop(s)
        x2 = heapq.heappop(s)
        if x1 != x2:
            heapq.heappush(s, x1 - x2)
    return -s[0] if s else 0



# 703. 数据流中的第 K 大元素

def __init__(self, k, nums):
    self.k = k
    self.heap = nums
    heapq.heapify(self.heap)
    while len(self.heap) > k:
        heapq.heappop(self.heap)

def add(self, val):
	if len(self.heap) < self.k:
        heapq.heappush(self.heap, val)
    elif self.heap[0] < val:
        heapq.heapreplace(self.heap, val)

    return self.heap[0]



# 264. 丑数 II
def nthUglyNumber(self, n: int) -> int:
    seen = {1}
    hp = [1]
    heapq.heapify(hp)
    for _ in range(n):
        cur = heapq.heappop(hp)
        for i in [2, 3, 5]:
            new = cur * i
            if new not in seen:
                seen.add(new)
                heapq.heappush(hp, new)
        
    return cur


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

































