862. 和至少为 K 的最短子数组


nums = [2, -1, -2, 5, 3]


nums = [-1, 1, 2, 4, -2, 6]



presum is monotonic
if no negative element







def shortestSubarray(self, nums: List[int], k: int) -> int:
    preSum = [0]
    n = len(nums)
    q = deque()
    res = len(nums) + 1

    for c in nums:
        preSum.append(preSum[-1] + c)

    for i in range(len(preSum)):
        num = preSum[i]
        curSum = preSum[i]
        while q and curSum - preSum[q[0]] >= k:
            res = min(res, i - q.popleft())
        while q and preSum[q[-1]] >= curSum:
            q.pop()
        q.append(i)

    return res if res < len(nums) + 1 else -1





def shortestSubarray(self, nums: List[int], k: int) -> int:
        ans = inf
        cur_s = 0
        q = deque([(0, -1)])
        for i, x in enumerate(nums):
            cur_s += x  # 计算前缀和
            while q and cur_s - q[0][0] >= k:
                ans = min(ans, i - q.popleft()[1])  # 优化一
            while q and q[-1][0] >= cur_s:
                q.pop()  # 优化二
            q.append((cur_s, i))
        return ans if ans < inf else -1




