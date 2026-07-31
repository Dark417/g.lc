# 347. 前 K 个高频元素

def topKFrequent(self, nums: List[int], k: int) -> List[int]:
    dic = Counter(nums)
    ks = [(e, dic[e]) for e in dic]
    ks.sort(reverse = True, key = lambda x: x[1])
    return [ks[i][0] for i in range(k)]































