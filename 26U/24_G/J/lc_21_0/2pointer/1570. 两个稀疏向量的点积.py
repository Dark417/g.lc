# 1570. 两个稀疏向量的点积

class SparseVector:
    def __init__(self, nums: List[int]):
        self.nums = nums
        self.index = set()
        for i in range(len(self.nums)):
            if self.nums[i] != 0:
                self.index.add(i)

    def dotProduct(self, vec: 'SparseVector') -> int:
        c = vec.index
        c = set.intersection(self.index,c)
        ans = 0
        for i in c:
            ans += vec.nums[i] * self.nums[i]
        return ans



class SparseVector:
    def __init__(self, nums: List[int]):
        self.dic={i:num for i,num in enumerate(nums) if num!=0}

    def dotProduct(self, vec: 'SparseVector') -> int:
        res=0
        for i in vec.dic:
            if i in self.dic:
                res+=self.dic[i]*vec.dic[i]
        return res


class SparseVector:
    def __init__(self, nums: List[int]):
        self.data = SortedDict()
        for i, val in enumerate(nums):
            if val != 0:
                self.data[i] = val

    def dotProduct(self, vec: 'SparseVector') -> int:
        a, b = self.data, vec.data
        if len(a) > len(b):
            a, b = b, a

        ans = 0
        for key, val in a.items():
            if key in b:
                ans += val * b[key]
        return ans


