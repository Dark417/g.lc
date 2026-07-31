# 239. 滑动窗口最大值


def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
    n = len(nums)
    q = [(-nums[i], i) for i in range(k)]
    heapq.heapify(q)

    ans = [-q[0][0]]
    for i in range(k, n):
        heapq.heappush(q, (-nums[i], i))
        while q[0][1] <= i - k:
            heapq.heappop(q)
        ans.append(-q[0][0])
    
    return ans



def maxSlidingWindow(self, nums, k):
    d = collections.deque()
    out = []
    for i, n in enumerate(nums):
        while d and nums[d[-1]] < n:
            d.pop()
        d += i,
        if d[0] == i - k:
            d.popleft()
        if i >= k - 1:
            out += nums[d[0]],
    return out

    
def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
    n = len(nums)
    q = collections.deque()
    for i in range(k):
        while q and nums[i] >= nums[q[-1]]:
            q.pop()
        q.append(i)

    ans = [nums[q[0]]]
    for i in range(k, n):
        while q and nums[i] >= nums[q[-1]]:
            q.pop()
        q.append(i)
        while q[0] <= i - k:
            q.popleft()
        ans.append(nums[q[0]])
    
    return ans





def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
    n = len(nums)
    prefixMax, suffixMax = [0] * n, [0] * n
    for i in range(n):
        if i % k == 0:
            prefixMax[i] = nums[i]
        else:
            prefixMax[i] = max(prefixMax[i - 1], nums[i])
    for i in range(n - 1, -1, -1):
        if i == n - 1 or (i + 1) % k == 0:
            suffixMax[i] = nums[i]
        else:
            suffixMax[i] = max(suffixMax[i + 1], nums[i])

    ans = [max(suffixMax[i], prefixMax[i + k - 1]) for i in range(n - k + 1)]
    return ans












