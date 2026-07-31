# 930. 和相同的二元子数组


def numSubarraysWithSum(self, nums: List[int], goal: int) -> int:
    cnt = 0
    presum = 0
    dc = dict()
    for num in nums:
        dc[presum] = dc.get(presum, 0) + 1
        presum += num
        if presum - goal in dc:
            cnt += dc[presum - goal]
    return cnt


def numSubarraysWithSum(self, nums: List[int], goal: int) -> int:
    n = len(nums)
    presum = [0] + list(accumulate(nums))
    hashmap = defaultdict(int, {0:1})
    ans = 0
    for i in range(n):
        r = presum[i+1]
        l = r - goal
        ans += hashmap[l]
        hashmap[r] += 1
    return ans


def numSubarraysWithSum(self, nums: List[int], goal: int) -> int:
    n = len(nums)
    ans = l1 = l2 = s1 = s2 = 0
    for r in range(n):
        s1 += nums[r]
        s2 += nums[r]
        while l1 <= r and s1 > goal:
            s1 -= nums[l1]
            l1 += 1
        while l2 <= r and s2 >= goal:
            s2 -= nums[l2]
            l2 += 1
        ans += l2 - l1
    return ans














