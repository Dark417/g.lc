




350. 两个数组的交集 II


3185. 构成整天的下标对数目 II


997. 找到小镇的法官
def findJudge(self, n: int, trust: List[List[int]]) -> int:
    from0 = [0] * (n + 1)
    to0 = [0] * (n + 1)

    for f, t in trust:
        from0[f] += 1
        to0[t] += 1
    for i in range(1, n + 1):
        if from0[i] == 0 and to0[i] == n - 1:
            return i
    return -1



1002. 查找共用字符

def commonChars(self, words: List[str]) -> List[str]:
        if not words:
            return []
        
        # Step 1: Use reduce to find common characters
        from functools import reduce
        common_chars = reduce(lambda x, y: x & set(y), words, set(words[0]) if words else set())
        
        # Step 2: Include each common character exactly once (skipping min_freq)
        result = list(common_chars)
        
        return result


def commonChars(self, words: List[str]) -> List[str]:
    minfreq = [float("inf")] * 26
    for word in words:
        freq = [0] * 26
        for ch in word:
            freq[ord(ch) - ord("a")] += 1
        for i in range(26):
            minfreq[i] = min(minfreq[i], freq[i])
    
    ans = list()
    for i in range(26):
        ans.extend([chr(i + ord("a"))] * minfreq[i])
    return ans





def commonChars(self, words: List[str]) -> List[str]:
	return list(reduce(lambda x, y: x & y, (Counter(word) for word in words)).elements())



return [char for char in set(words[0]) for _ in range(min(word.count(char) for word in words)) if char in set(''.join(words[1:]))] if words else []










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
        res[i] = 0 if not nums[i] else cnt[nums[i] - 1]
        
    return res





1656. 设计有序流

class OrderedStream:

    def __init__(self, n: int):
        self.stream = [""] * (n + 1)
        self.ptr = 1
        

    def insert(self, idKey: int, value: str) -> List[str]:
        self.stream[idKey] = value
        res = []
        while self.ptr < len(self.stream) and self.stream[self.ptr]:
            res.append(self.stream[self.ptr])
            self.ptr += 1
        return res



2475. 数组中不等三元组的数目
def unequalTriplets(self, nums: List[int]) -> int:
        nums.sort()
        res = 0
        n = len(nums)
        i = j = 0
        while i < n:
            while j < n and nums[j] == nums[i]:
                j += 1
            res += i * (j - i) * (n - j)
            i = j
        return res


def unequalTriplets(self, nums: List[int]) -> int:
    count = Counter(nums)
    res = t = 0
    n = len(nums)
    for _, v in count.items():
        res += t * v * (n - t - v)
        t += v
    return res


953. 验证外星语词典
def isAlienSorted(self, words: List[str], order: str) -> bool:
    idx = {c: i for i, c in enumerate(order)}
    return all(s <= t for s, t in pairwise([idx[c] for c in word] for word in words))






3185. 构成整天的下标对数目 II
    for h in hours:
        res += cnt[(24 - h % 24) % 24]
        cnt[h % 24] += 1

    1497. 检查数组对是否可以被 k 整除






##########################################################################################
# mid

442. 数组中重复的数据
class Solution:
    def findDuplicates(self, nums: List[int]) -> List[int]:
        for i in range(len(nums)):
            print(i)
            while nums[i] != nums[nums[i] - 1]:
                nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]
            
        return [num for i, num in enumerate(nums) if num - 1 != i]


0
4 7
[7, 3, 2, 4, 8, 2, 3, 1]
7 3
[3, 3, 2, 4, 8, 2, 7, 1]
3 2
[2, 3, 3, 4, 8, 2, 7, 1]
2 3
[3, 2, 3, 4, 8, 2, 7, 1]
1
2
3
4
8 1
[3, 2, 3, 4, 1, 2, 7, 8]
1 3
[1, 2, 3, 4, 3, 2, 7, 8]
5
6
7

































































































































































































































































































































































































































































