# 2025.7.27
# 害lc呢？
# 3heap

#ez####################################################################
LCR 159. 库存管理 III


3318. 计算子数组的 x-sum I


703. 数据流中的第 K 大元素



1464. 数组中两元素的最大乘积


2099. 找到和最大的长度为 K 的子序列


	1005. K 次取反后最大化的数组和
	!!!


2335. 装满杯子需要的最短总时长


2357. 使数组中所有元素都等于零

506. 相对名次


1046. 最后一块石头的重量


1086. 前五科的均分


1337. 矩阵中战斗力最弱的 K 行

3507. 移除最小数对使数组有序 I


2231. 按奇偶性交换后的最大数字



2500. 删除每行中的最大值



2558. 从数量最多的堆取走礼物





2974. 最小数字游戏








#mid####################################################################


215. 数组中的第K个最大元素
!!!!
    
    692. 前K个高频单词

    

912. 排序数组
!!!!


347. 前 K 个高频元素
!!



面试题 17.14. 最小K个数
quick sort!!!!



378. 有序矩阵中第 K 小的元素





#ez####################################################################




LCR 159. 库存管理 III
def inventoryManagement(self, stock: List[int], cnt: int) -> List[int]:
    #heap = stock.copy()
    heapify(heap)  # Convert to min-heap in-place
    def pop_from_heap(_):
        return heappop(heap)
    res = list(map(pop_from_heap, range(cnt)))
    return res

    heapify(stock)
    res = list(map(lambda x: heappop(stock), range(cnt)))
    return res

def inventoryManagement(self, stock: List[int], cnt: int) -> List[int]:
    if cnt == 0:
        return []
    hp = [-x for x in stock[:cnt]]
    heapq.heapify(hp)
    for i in range(cnt, len(stock)):
        if -hp[0] > stock[i]:
            heapq.heappop(hp)
            heapq.heappush(hp, -stock[i])
    return [-x for x in hp]





3318. 计算子数组的 x-sum I
return [sum(k * v for k, v in sorted([v, k] for k, v in Counter(nums[i : i + k]).items())[-x :]) for i in range(len(nums) - k + 1)]

def findXSum(self, nums: List[int], k: int, x: int) -> List[int]:
    n = len(nums)
    res = []
    cnt = Counter(nums[:k])
    for i in range(n - k + 1):
        if i > 0:
            cnt[nums[i- 1]] -= 1
            if cnt[nums[i - 1]] == 0:
                del cnt[nums[i - 1]]
            cnt[nums[i + k - 1]] += 1
        most_common = list(sorted(cnt.items(), key = lambda itm: (itm[1], itm[0]), reverse=True))
        top_x = most_common[:min(len(most_common), x)]
        res.append(sum(k*v for k, v in top_x))
    return res

def findXSum(self, nums: List[int], k: int, x: int) -> List[int]:
    ans = []
    if len(nums) < k:
        return sum(nums)
    for i in  range(len(nums) - k + 1):
        cnt = Counter(nums[i:i+k])
        most_common = sorted(cnt.items(),key = lambda item:(-item[1],-item[0]))
        top_x = [item[0] for item in most_common]
        tmp=0
        for j in range(min(len(top_x),x)):
            tmp += top_x[j]*cnt[top_x[j]]
        ans.append(tmp)
    return ans



703. 数据流中的第 K 大元素


def __init__(self, k, nums):
    self.k = k
    self.que = nums
    heapq.heapify(self.que)

def add(self, val):

    heapq.heappush(self.que, val)
    while len(self.que) > self.k:
        heapq.heappop(self.que)
    return self.que[0]




def __init__(self, k: int, nums: List[int]):
    self.hp = nums
    self.k = k
    heapq.heapify(self.hp)
    while len(self.hp) > k:
        heapq.heappop(self.hp)

def add(self, val: int) -> int:
    if len(self.hp) < self.k:
        heapq.heappush(self.hp, val)
    elif self.hp[0] < val:
        heapq.heapreplace(self.hp, val)
    
    return self.hp[0]


def __init__(self, k: int, nums: List[int]):
    self.k = k
    self.q = q =[] 
    for x in nums:
        heappush(q,x)
        if len(q) > k:
            heappop(q)

def add(self, val: int) -> int:
    q = self.q
    heappush(q,val)
    if len(q) > self.k:
        heappop(q)
    return q[0]




1464. 数组中两元素的最大乘积
def maxProduct(self, nums: List[int]) -> int:
    a, b = nums[0], nums[1]
    if a < b:
        a, b = b, a
    for i in range(2, len(nums)):
        num = nums[i]
        if num > a:
            a, b = num, a
        elif num > b:
            b = num
    return (a - 1) * (b - 1)

	heapify(nums)
    li = nlargest(2,nums)
    return (li[0]-1)*(li[1]-1)




2099. 找到和最大的长度为 K 的子序列
def maxSubsequence(self, nums: List[int], k: int) -> List[int]:
    n = len(nums)
    vals = [[i, nums[i]] for i in range(n)]
    vals.sort(key = lambda x: x[1], reverse=True)
    ns = sorted(vals[:k])
    return [v for _, v in ns]

def maxSubsequence(self, nums: List[int], k: int) -> List[int]:
    idx = sorted(range(len(nums)), key = lambda i: nums[i])
    idx = sorted(idx[-k:])
    return [nums[i] for i in idx]

    idx = sorted(range(len(nums)), key = lambda i: nums[i], reverse = True)
    idx = sorted(idx[:k])



    1005. K 次取反后最大化的数组和
    def largestSumAfterKNegations(self, nums: List[int], k: int) -> int:
        heapq.heapify(nums)

        for i in range(k):
            top = -nums[0]
            heapq.heapreplace(nums, top)
        return sum(nums)


    # public int largestSumAfterKNegations(int[] nums, int k) {
    #     int n = nums.length;
    #     int res = 0;
    #     PriorityQueue<Integer> heap = new PriorityQueue<>(new Comparator<Integer>(){
    #         public int compare(Integer p1, Integer p2) {
    #             return p1 - p2;
    #         }
    #     });
    #     for(int i =0;i < n;i++){
    #         heap.offer(nums[i]);
    #         res += nums[i];
    #     }
    #     for(int i = 0;i < k;i++){
    #         int num = heap.poll();
    #         res -= 2*num;
    #         num = -num;
    #         heap.offer(num);
    #     }
    #     return res;
    # }




    def largestSumAfterKNegations(self, nums: List[int], k: int) -> int:
        freq = Counter(nums)
        res = sum(nums)
        for i in range(-100, 0):
            if freq[i]:
                ops = min(k, freq[i])
                res += -i * ops * 2
                freq[i] -= k
                freq[-i] += k
                k -= ops
                if k == 0:
                    break

        if k > 0 and not k // 2 and not freq[0]:
            for i in range(1, 101):
                if freq[i]:
                    res -= i * 2
                    break
        return res


    def largestSumAfterKNegations(self, nums: List[int], k: int) -> int:
        freq = Counter(nums)
        for i in range(-100, 0):
            if freq[i]:
                ops = min(k, freq[i])
                freq[i] -= ops
                freq[-i] += ops
                k -= ops
                if k == 0:
                    break

        if k > 0 and k % 2 == 1 and not freq[0]:
            for i in range(1, 101):
                if freq[i]:
                    freq[i] -= 1
                    freq[-i] += 1
                    break
        return sum(n* cfor n, c in freq.items())


2335. 装满杯子需要的最短总时长
def fillCups(self, amount: List[int]) -> int:
    from queue import PriorityQueue as PQ
    pq = PQ()
    for n in amount:
        pq.put(-n)
    res = 0
    while 1:
        v1 = pq.get()
        v2 = pq.get()
        if v1 == 0 and v2 == 0:
            break
        if v1 < 0 and v2 < 0:
            v1 += 1
            v2 += 1
        elif v1 < 0:
            v1 += 1
        res += 1
        pq.put(v1)
        pq.put(v2)
    return res





2357. 使数组中所有元素都等于零
def minimumOperations(self, nums: List[int]) -> int:
    heapify(nums)
    res = 0
    while nums:
        val = 0
        while nums:
            val = heappop(nums)
            if val != 0:
                break
        for i in range(len(nums)):
            nums[i] -= val
        if val != 0:
            res += 1
    return res

    return len(set(nums) - {0})

def minimumOperations(self, nums: List[int]) -> int:
    nums.sort()
    ans = 0
    prev = 0
    for num in nums:
        if num > prev:
            ans += 1
            prev = num
    return ans

def minimumOperations(self, nums: List[int]) -> int:
    heapify(nums)
    ans = 0
    while nums:
        val = heappop(nums)
        if val == 0:
            continue
        ans += 1
        new_nums = [x - val for x in nums]
        nums[:] = new_nums
        heapify(nums)
    return ans


506. 相对名次
def findRelativeRanks(self, score: List[int]) -> List[str]:
    desc = ("Gold Medal", "Silver Medal", "Bronze Medal")
    ans = [""] * len(score)
    arr = sorted(enumerate(score), key=lambda x: -x[1])
    for i, (idx, _) in enumerate(arr):
        ans[idx] = desc[i] if i < 3 else str(i + 1)
    return ans


def findRelativeRanks(self, score: List[int]) -> List[str]:
    ranks = sorted(score, reverse=True)
    ranksIndex = dict()
    for i in range(len(ranks)):
        ranksIndex[ranks[i]] = i
    res = []
    for s in score:
        rank = ranksIndex[s]
        if rank == 0:
            res.append("Gold Medal")
        elif rank == 1:
            res.append("Silver Medal")
        elif rank == 2:
            res.append("Bronze Medal")
        else:
            res.append(str(rank + 1))
    return res


def findRelativeRanks(self, nums):
    heap = [(-num, i) for i, num in enumerate(nums)]
    heapq.heapify(heap)
    N = len(nums)
    res = [""] * N
    count = 1
    while heap:
        num, i = heapq.heappop(heap)
        if count == 1:
            res[i] = "Gold Medal"
        elif count == 2:
            res[i] = "Silver Medal"
        elif count == 3:
            res[i] = "Bronze Medal"
        else:
            res[i] = str(count)
        count += 1
    return res



1046. 最后一块石头的重量
def lastStoneWeight(self, stones: List[int]) -> int:
    heap = [-stone for stone in stones]
    heapify(heap)
    while len(heap) > 1:
        x = heappop(heap)
        y = heappop(heap)
        if x != y:
            heappush(heap, x-y)
    if heap:
        return -heap[0]
    return 0



1086. 前五科的均分
def highFive(self, items: List[List[int]]) -> List[List[int]]:
    heap = {}
    for id, score in items:
        if id not in heap:
            heap[id] = []
        heappush(heap[id], - score)
    
    res = []
    for id, score in heap.items():
        sm = 0
        for i in range(5):
            sm += -1 * heappop(score)
        res.append([id, sm//5])
    return sorted(res, key = lambda x: x[0])


def highFive(self, items: List[List[int]]) -> List[List[int]]:
    items.sort(key = lambda x: [-x[0], x[1]], reverse = True)
    dc = defaultdict(list)
    for id, score in items:
        if len(dc[id]) < 5:
            dc[id].append(score)
            
    return [[id, sum(dc[id])//5] for id in dc.keys()]


    def highFive(self, items: List[List[int]]) -> List[List[int]]:
        d = defaultdict(list)
        for i, s in items:
            d[i].append(s)
        return [[k, sum(nlargest(5, d[k]))//5] for k in sorted(d.keys())]



1337. 矩阵中战斗力最弱的 K 行
def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
    m, n = len(mat), len(mat[0])
    power = []
    for i in range(m):
        l, r, pos = 0, n - 1, -1
        while l <= r:
            mid = (l + r) // 2
            if mat[i][mid] == 0:
                r = mid - 1
            else:
                pos = mid
                l = mid + 1
        power.append([pos, i])

    heapify(power)
    res = []
    for _ in range(k):
        res.append(heappop(power)[1])
    return res


2231. 按奇偶性交换后的最大数字
def largestInteger(self, num: int) -> int:
    s = str(num)
    ans = 0
    # maxHeap[0] := the odd digits
    # maxHeap[1] := the even digits
    maxHeap = [[] for _ in range(2)]

    for c in s:
      digit = int(c)
      heapq.heappush(maxHeap[digit % 2], -digit)

    for c in s:
      i = int(c) & 1
      ans = (ans * 10 - heapq.heappop(maxHeap[i]))

    return ans





2500. 删除每行中的最大值
def deleteGreatestValue(self, grid: List[List[int]]) -> int:
        for row in grid:
            row.sort()
        return sum(map(max, zip(*grid)))



2558. 从数量最多的堆取走礼物
def pickGifts(self, gifts: List[int], k: int) -> int:
    q = [-gift for gift in gifts]
    heapify(q)
    while k:
        # x = heappop(q)
        # heappush(q, -int(sqrt(-x)))
        heapreplace(gifts, -isqrt(-gifts[0]))
        k -= 1
    return -sum(q)




3507. 移除最小数对使数组有序 I





2974. 最小数字游戏
def numberGame(self, nums: List[int]) -> List[int]:
        heapify(nums)
        res = []
        while nums:
            a = heappop(nums)
            b = heappop(nums)
            res.append(b)
            res.append(a)
        return res




####################################################################
215. 数组中的第K个最大元素
    

    692. 前K个高频单词
    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        cnt = Counter(words)
        # sort on lambda
        srted = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))

        return [x[0] for x in srted[:k]]

    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        hash = collections.Counter(words)
        # sorted on key < = sort on cnt
        res = sorted(hash, key=lambda word:(-hash[word], word))
        return res[:k]


    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        cnt = Counter(words)
        h = []
        for ke, v in cnt.items():
            heappush(h, (-v, ke))
        res = []
        for _ in range(k):
            res.append(heapq.heappop(h)[1]) # We only want the word
        return res





912. 排序数组






347. 前 K 个高频元素
def topKFrequent(self, nums: List[int], k: int) -> List[int]:
    cnt = Counter(nums)
    maxcnt = max(cnt.values())
    buckets = [[] for _ in range(maxcnt + 1)]
    for x, c in cnt.items():
        buckets[c].append(x)
    res = []

    for bucket in reversed(buckets):
        res += bucket
        if len(res) == k:
            return res


    451. 根据字符出现频率排序
    def frequencySort(self, s: str) -> str:
        cnt = defaultdict(list)
        for c in s:
            cnt[c].append(c)
        
        sorted_items = sorted(cnt.items(), key = lambda x: len(x[1]), reverse = True)
        return "".join("".join(x[1]) for x in sorted_items)

    return ''.join([i * j for i, j in collections.Counter(s).most_common()])






面试题 17.14. 最小K个数
def smallestK(self, arr: List[int], k: int) -> List[int]:
    if k == 0:
        return []
    hp = [-x for x in arr[:k]]
    heapify(hp)
    for i in range(k, len(arr)):
        if -hp[0] > arr[i]:
            heappop(hp)
            heappush(hp, -arr[i])
    return [-x for x in hp]


378. 有序矩阵中第 K 小的元素



451. 根据字符出现频率排序








































































































































































































































