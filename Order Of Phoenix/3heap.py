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


#mid####################################################################











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



























































































































































































































































































































