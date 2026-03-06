





pre[i]=pre[i−1]+nums[i]

pre[i]−pre[j−1]==k

pre[j−1]==pre[i]−k



##########################################################################################
# ez


1480. 一维数组的动态和
数组前缀和

def runningSum(self, nums: List[int]) -> List[int]:
    res = [nums[0]]
    for i in range(1, len(nums)):
        res.append(res[-1] + nums[i])
    return res


def runningSum(self, nums: List[int]) -> List[int]:
    for i in range(1, len(nums)):
        nums[i] += nums[i - 1]
    return nums


def runningSum(self, nums: List[int]) -> List[int]:
    dp = [0] * len(nums)
    dp[0] = nums[0]
    for i in range(1, len(nums)):
        dp[i] = dp[i - 1] + nums[i]
    return dp

from itertools import accumulate
return list(itertools.accumulate(nums))
return list(accumulate(nums))

reduce(lambda acc, x: acc + [acc[-1] + x], nums[1:], [nums[0]]) 
# (uses lambda and reduce, O(n²)).

[sum(nums[:i+1]) for i in range(len(nums))] 
#(list comprehension, O(n²)).



reduce(lambda acc, x: acc + [add(acc[-1], x)], nums[1:], [nums[0]]) 
#(uses operator.add, O(n²)).

list(itertools.accumulate(nums, lambda x, y: x + y)) #(custom lambda, O(n)).

np.cumsum(nums).tolist() 
#(NumPy, O(n), requires NumPy).



303. 区域和检索 - 数组不可变
设计数组前缀和

class NumArray:
	def __init__(self, nums: List[int]):
	    self.sums = [0]
	    _sums = self.sums

	    for num in nums:
	        _sums.append(_sums[-1] + num)

	def sumRange(self, i: int, j: int) -> int:
	    _sums = self.sums
	    return _sums[j + 1] - _sums[i]

class NumArray:
    def __init__(self, nums: List[int]):
        s = [0] * (len(nums) + 1)
        for i, x in enumerate(nums):
            s[i + 1] = s[i] + x
        self.s = s

    def sumRange(self, left: int, right: int) -> int:
        return self.s[right + 1] - self.s[left]




2389. 和有限的最长子序列
贪心数组二分查找前缀和排序
def answerQueries(self, nums: List[int], queries: List[int]) -> List[int]:
    def bs(nums, t):
        l, r = 0, len(nums)
        while l < r:
            m = (l + r) // 2
            if t < nums[m]:
                r = m
            else:
                l = m + 1
        return l

    nums.sort()
    res = [0] * len(queries)
    for i in range(1, len(nums)):
        nums[i] += nums[i - 1]
    
    for i in range(len(queries)):
        q = queries[i]
        res[i] = bs(nums, q)

    return res


    1365. 有多少小于当前数字的数字
    	def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
	        cnt = [0] * 101
	        n = len(nums)
	        for i in range(n):
	            cnt[nums[i]] += 1
	        for i in range(1, 101):
	            cnt[i] += cnt[i-1]
	        
	        res = [0] * n
	        for i in range(n):
	            res[i] = 0 if nums[i]==0 else cnt[nums[i] - 1]

	        return res


724. 寻找数组的中心下标
数组前缀和

def pivotIndex(self, nums: List[int]) -> int:
    s = 0
    sm = sum(nums)
    for i in range(len(nums)):
        n = nums[i]
        if s * 2 + n == sm:
            return i
        s += n
    return -1

    1991. 找到数组的中间位置

    2574. 左右元素和的差值
    数组前缀和
    def leftRightDifference(self, nums: List[int]) -> List[int]:
        left_sum, right_sum = 0, sum(nums)
        for i, x in enumerate(nums):
            right_sum -= x
            nums[i] = abs(left_sum - right_sum)
            left_sum += x
        return nums


1422. 分割字符串的最大得分
字符串前缀和
def maxScore(self, s: str) -> int:
    right1 = s.count('1')
    ans = left0 = 0
    for c in s[:-1]:
        if c == '0':
            left0 += 1
        else:  # c == '1'
            right1 -= 1
        ans = max(ans, left0 + right1)
    return ans


def maxScore(self, s: str) -> int:
    score = s.count('1')
    ans = 0
    for c in s[:-1]:
        score += 1 if c == '0' else -1
        ans = max(ans, score)
    return ans








2485. 找出中枢整数
数学前缀和

def pivotInteger(self, n: int) -> int:
    for x in range(1, n + 1):
        if (1 + x) * x == (x + n) * (n - x + 1):
            return x
    return -1



1854. 人口最多的年份
数组计数前缀和





3427. 变长子数组求和
数组前缀和
!!!
def subarraySum(self, nums: List[int]) -> int:
    presum = [0]
    for i in range(len(nums)):
        presum.append(presum[-1] + nums[i])
    res = 0
    for i in range(len(nums)):
        res += presum[i + 1] - presum[max(0, i - nums[i])]
    return res



1413. 逐步求和得到正数的最小值
数组前缀和

def minStartValue(self, nums: List[int]) -> int:
    presum = [0]
    for i in range(len(nums)):
        presum.append(presum[-1] + nums[i])
    mn = min(presum)
    if mn < 1:
        for i in range(len(presum)):
            if presum[i] == mn:
                return 1 - presum[i]


1732. 找到最高海拔
数组前缀和
def largestAltitude(self, gain: List[int]) -> int:
    return max(accumulate(gain, initial=0))



1588. 所有奇数长度子数组的和
!
数组数学前缀和
def sumOddLengthSubarrays(self, arr: List[int]) -> int:
    sum = 0
    n = len(arr)
    for start in range(n):
        length = 1
        while start + length <= n:
            for v in arr[start:start + length]:
                sum += v
            length += 2
    return sum


def sumOddLengthSubarrays(self, arr: List[int]) -> int:
    presum = [0]
    res = 0
    for i in range(len(arr)):
        presum.append(presum[-1] + arr[i])
    for start in range(len(arr)):
        length = 1
        while start + length <= len(arr):
            end = start + length - 1 ###
            res += presum[end + 1] - presum[start] ###
            length += 2
    return res 



3354. 使数组元素等于零
数组前缀和模拟





3364. 最小正和子数组
数组前缀和滑动窗口





1893. 检查是否区域内所有整数都被覆盖
数组哈希表前缀和

def isCovered(self, ranges: List[List[int]], left: int, right: int) -> bool:
    diff = [0] * 52   # 差分数组
    for l, r in ranges:
        diff[l] += 1
        diff[r+1] -= 1
    # 前缀和
    curr = 0
    for i in range(1, 51):
        curr += diff[i]
        if left <= i <= right and curr <= 0:
            return False
    return True


def isCovered(self, ranges: List[List[int]], left: int, right: int) -> bool:
    line = [0] * 51
    for start, end in ranges:
        for i in range(start, end + 1):
            line[i] += 1
    for i in range(left, right + 1):
        if line[i] == 0:
            return False
    return True




2848. 与车相交的点
数组哈希表前缀和





3028. 边界上的蚂蚁
数组前缀和模拟




3432. 统计元素和差值为偶数的分区方案
数组数学前缀和







##########################################################################################
# mid


560. 和为 K 的子数组
!!!
def subarraySum(self, nums: List[int], k: int) -> int:
    res = s = 0
    cnt = defaultdict(int)
    cnt[0] = 1
    for n in nums:
        s += n
        res += cnt[s - k]
        cnt[s] += 1
    return res


def subarraySum(self, nums: List[int], k: int) -> int:
	s = [0] * (len(nums) + 1)
	for i, x in enumerate(nums):
	    s[i + 1] = s[i] + x

	ans = 0
	cnt = defaultdict(int)
	for sj in s:
	    ans += cnt[sj - k]
	    cnt[sj] += 1
	return ans


    523. 连续的子数组和
    !!
    def checkSubarraySum(self, nums: List[int], k: int) -> bool:
        history = {0}
        prev = 0
        for i, s in enumerate(accumulate(nums)):
            if i > 0 and s % k in history:
                return True
            history.add(prev)
            prev = s % k
        return False

    def checkSubarraySum(self, nums: List[int], k: int) -> bool:
        modes = set()
        presum = 0
        for num in nums:
            last = presum
            presum += num
            presum %= k
            if presum in modes:
                return True
            modes.add(last)
        return False

    def checkSubarraySum(self, nums, k):
        d = {0: -1}
        pre = 0
        for index, num in enumerate(nums):
            pre += num
            rem = pre % k
            i = d.get(rem, index)
            if i == index:
                d[rem] = index
            elif i <= index - 2:
                return True
        return False


    713. 乘积小于 K 的子数组
    !!
    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        ans, prod, i = 0, 1, 0
        for j, num in enumerate(nums):
            prod *= num
            while i <= j and prod >= k:
                prod //= nums[i]
                i += 1
            ans += j - i + 1
        return ans

    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        if k <= 1: return 0
        res = 0
        start = 0
        pdt = 1
        for end, val in enumerate(nums):
            pdt *= val
            while pdt >= k:
                pdt /= nums[start]
                start += 1
            res += end - start + 1
        return res

    !!
    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        if k == 0:
            return 0
        ans, n = 0, len(nums)
        logPrefix = [0] * (n + 1)
        for i, num in enumerate(nums):
            logPrefix[i + 1] = logPrefix[i] + log(num)
        for j in range(1, n + 1):
            l = bisect_right(logPrefix, logPrefix[j] - log(k) + 1e-10, 0, j)
            ans += j - l
        return ans


    974. 和可被 K 整除的子数组
    def subarraysDivByK(self, nums: List[int], k: int) -> int:
        cnt = {0: 1}
        premod = res = 0
        for num in nums:
            premod = (premod + num) % k
            if premod < 0:
                premod += k
            res = cnt.get(premod, 0)
            cnt[premod] = cnt.get(premod, 0) + 1
        return res


    325. 和等于 k 的最长子数组长度
    !!
    def maxSubArrayLen(self, nums: List[int], k: int) -> int:
    prefix_sum = 0
    longest_subarray = 0
    indices = {0: -1}
    for i, num in enumerate(nums):
        prefix_sum += num 
        if prefix_sum - k in indices:
            longest_subarray = max(longest_subarray, i - indices[prefix_sum - k])
        if prefix_sum not in indices:
            indices[prefix_sum] = i
    return longest_subarray


238. 除自身以外数组的乘积
def productExceptSelf(self, nums: List[int]) -> List[int]:
    n = len(nums)
    lprod = [1] * n
    rprod = [1] * n

    for i in range(1, n):
        lprod[i] = lprod[i - 1] * nums[i - 1]

    print(n)
    for i in reversed(range(n - 1)):
        print(i, i+ 1)
        rprod[i] = rprod[i + 1] * nums[i + 1]

    res = [1] * n
    for i in range(n):
        res[i] = lprod[i] * rprod[i]
    return res


def productExceptSelf(self, nums: List[int]) -> List[int]:
    length = len(nums)
    answer = [0]*length
    
    answer[0] = 1
    for i in range(1, length):
        answer[i] = nums[i - 1] * answer[i - 1]
    

    R = 1;
    for i in reversed(range(length)):
        answer[i] = answer[i] * R
        R *= nums[i]
    
    return answer


1208. 尽可能使字符串相等
!!
def equalSubstring(self, s: str, t: str, maxCost: int) -> int:
    n = len(s)
    accDiff = [0] + list(accumulate(abs(ord(sc) - ord(tc)) for sc, tc in zip(s, t)))
    res = 0
    for i in range(1, n + 1):
        start = bisect_left(accDiff, accDiff[i] - maxCost)
        res = max(res, i - start)
    return res


2750. 将数组划分成若干好子数组的方式
def numberOfGoodSubarraySplits(self, nums: List[int]) -> int:
    mod = 10**9 + 7
    res = 1
    pre = -1
    for i, n in enumerate(nums):
        if n == 0:
            continue
        if pre >= 0:
            res = res * (i - pre) % mod
        pre = i
    return 0 if pre < 0 else res


930. 和相同的二元子数组
def numSubarraysWithSum(self, nums: List[int], goal: int) -> int:
    # n = len(nums)
    # presum = [0] + list(accumulate(nums))
    # hashmap = defaultdict(int, {0:1})
    # ans = 0
    # for i in range(n):
    #     end = presum[i+1]
    #     start = end - goal
    #     ans += hashmap[start]
    #     hashmap[end] += 1
    # return ans

    n = len(nums)
    presum = [0] + list(accumulate(nums))
    hashmap = defaultdict(int, {0:1})
    ans = 0
    for i in range(n):
        ans += hashmap[presum[i+1] - goal]
        hashmap[presum[i+1]] += 1
    return ans

    def numSubarraysWithSum(self, nums: List[int], goal: int) -> int:
        res = sm = 0
        cnt = defaultdict(int, {0:1})
        for num in nums:
            sm += num
            res += cnt.get(sm - goal, 0)
            cnt[sm] += 1
        return res
        
    def numSubarraysWithSum(self, nums: List[int], goal: int) -> int:
        res = sm = 0
        cnt = {}
        for num in nums:
            cnt[sm] = cnt.get(sm, 0) + 1
            sm += num
            res += cnt.get(sm - goal, 0)
        return res




















































































