
#diff array

1094. 拼车
1109. 航班预订统计
2381. 字母移位 II
2406. 将区间分为最少组数
2772. 使数组中的所有元素都等于零
2528. 最大化城市的最小供电站数目

3355. 零数组变换 I


#intervals




1094. 拼车
def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
    to_max = max(trip[2] for trip in trips)
    diff = [0] * (to_max + 1)

    for n, f, t in trips:
        diff[f] += n
        diff[t] -= n
    
    cnt = 0

    for i in range(to_max + 1):
        cnt += diff[i]
        if cnt > capacity:
            return False
            
    return True


    def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
	    records = sorted(itertools.chain.from_iterable(((dst, -num), (src, num)) for num, src, dst in trips))
	    return all(carry <= capacity for carry in itertools.accumulate(map(lambda x: x[1], records)))

	def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
        d = [0] * 1001
        for num, from_, to in trips:
            d[from_] += num
            d[to] -= num
        return all(s <= capacity for s in accumulate(d))

作者：灵茶山艾府
链接：https://leetcode.cn/problems/car-pooling/solutions/2550264/suan-fa-xiao-ke-tang-chai-fen-shu-zu-fu-9d4ra/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。




1109. 航班预订统计
def corpFlightBookings(self, bookings: List[List[int]], n: int) -> List[int]:
    nums = [0] * n
    for left, right, inc in bookings:
        nums[left - 1] += inc
        if right < n:
            nums[right] -= inc

    for i in range(1, n):
        nums[i] += nums[i - 1]
    
    return nums


2381. 字母移位 II

def shiftingLetters(self, s: str, shifts: List[List[int]]) -> str:
    c2i = {c: i for i, c in enumerate(ascii_lowercase)}
    diff = [0] * (len(s) + 1)
    for start, end, dir in shifts:
        diff[start] += dir * 2 - 1
        diff[end + 1] -= dir * 2 - 1
    return ''.join(ascii_lowercase[(c2i[c] + shift) % 26] for c, shift in zip(s, accumulate(diff)))

    c2i = {c: i for i, c in enumerate(ascii_lowercase)}
    diff = [0] * (len(s) + 1)
    for s, e, d in shifts:
        diff[s] += d * 2 - 1
        diff[e + 1] -= d * 2 - 1
    return ''.join(ascii_lowercase[(c2i[c] + shift) % 26] for c, shift in zip(s, accumulate(diff)))


2406. 将区间分为最少组数
def minGroups(self, intervals: List[List[int]]) -> int:
    intervals.sort(key=lambda p: p[0])
    h = []
    for left, right in intervals:
        if h and left > h[0]:
        	heapreplace(h, right)
        else:
        	heappush(h, right)
    return len(h)



2772. 使数组中的所有元素都等于零
def checkArray(self, nums: List[int], k: int) -> bool:
    n = len(nums)
    diff = [0] * (n + 1)
    sum_d = 0
    for i, x in enumerate(nums):
        sum_d += diff[i]
        x += sum_d
        if x == 0:
            continue
        if x < 0 or i + k > n:
            return False
        sum_d -= x
        diff[i + k] += x
    return True



370. 区间加法
def getModifiedArray(self, length: int, updates: List[List[int]]) -> List[int]:
    arr = [0] * length
    for s, e, i in updates:
        arr[s] += i
        if e + 1 < length:
            arr[e + 1] -= i
    for i in range(1, length):
        arr[i] += arr[i - 1]
    return arr













2848. 与车相交的点
def numberOfPoints(self, nums: List[List[int]]) -> int:
    c = max(e for _, e in nums)
    diff = [0] * (c + 2)
    for s, e in nums:
        diff[s] += 1
        diff[e + 1] -= 1
    res = cnt = 0
    for i in range(1, c + 1):
        cnt += diff[i]
        if cnt > 0:
            res += 1
    return res






3355. 零数组变换 I
def isZeroArray(self, nums: List[int], queries: List[List[int]]) -> bool:
    diff = [0] * (len(nums) + 1)
    for l, r in queries:
        diff[l] += 1
        diff[r + 1] -= 1
    for x, sum_d in zip(nums, accumulate(diff)):
        if x > sum_d:
            return False
    return True





##############################################################################
#intervals

56. 合并区间
def merge(self, intervals: List[List[int]]) -> List[List[int]]:
    intervals.sort(key = lambda x: x[0])
    merged = []
    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])
    return merged


	



252. 会议室
def canAttendMeetings(self, intervals: List[List[int]]) -> bool:
    intervals.sort()
    for i in range(len(intervals) - 1):
        if intervals[i][1] > intervals[i+1][0]:
            return False
    return True


253. 会议室 II





























