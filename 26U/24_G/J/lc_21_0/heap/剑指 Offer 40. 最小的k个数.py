# 剑指 Offer 40. 最小的k个数

def getLeastNumbers(self, arr: List[int], k: int) -> List[int]:
    arr.sort()
    return arr[:k]


def getLeastNumbers(self, arr: List[int], k: int) -> List[int]:
    heapq.heapify(arr)
    res = []
    for _ in range(k):
        res.append(heapq.heappop(arr))
    return res


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


def partition(self, nums, l, r):
    pivot = nums[r]
    i = l - 1
    for j in range(l, r):
        if nums[j] <= pivot:
            i += 1
            nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1], nums[r] = nums[r], nums[i + 1]
    return i + 1

def randomized_partition(self, nums, l, r):
    i = random.randint(l, r)
    nums[r], nums[i] = nums[i], nums[r]
    return self.partition(nums, l, r)

def randomized_selected(self, arr, l, r, k):
    pos = self.randomized_partition(arr, l, r)
    num = pos - l + 1
    if k < num:
        self.randomized_selected(arr, l, pos - 1, k)
    elif k > num:
        self.randomized_selected(arr, pos + 1, r, k - num)

def getLeastNumbers(self, arr: List[int], k: int) -> List[int]:
    if k == 0:
        return list()
    self.randomized_selected(arr, 0, len(arr) - 1, k)
    return arr[:k]




























