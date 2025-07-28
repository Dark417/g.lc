# 216. 组合总和 III



return [c for c in combinations(range(1, 10), k) if sum(c) == n]


def combinationSum3(self, k, n):
    def combs(k, n, cap):
        if not k:
            return [[]] * (not n)
        return [comb + [last]
                for last in range(1, cap)
                for comb in combs(k-1, n-last, last)]
    return combs(k, n, 10)


def combinationSum3(self, k, n):
    combs = [[]]
    for _ in range(k):
        combs = [[first] + comb
                 for comb in combs
                 for first in range(1, comb[0] if comb else 10)]
    return [c for c in combs if sum(c) == n]



def combinationSum3(self, k, n):
    return [c for c in
            reduce(lambda combs, _: [[first] + comb
                                     for comb in combs
                                     for first in range(1, comb[0] if comb else 10)],
                   range(k), [[]])
            if sum(c) == n]


                   
def combinationSum3(self, k: int, n: int) -> List[List[int]]:
    def dfs(start, cur, k, target):
        if k == 0 and target == 0:
            res.append(cur)
            return
        for i in range(start, 10):
            if i > target:
                return
            if target - i >= 0:
                dfs(i + 1, cur + [i], k - 1, target - i)
    
    res = []
    dfs(1, [], k, n)
    return res




# https://leetcode-cn.com/problems/combination-sum-iii/solution/zu-he-zong-he-iii-by-leetcode-solution/



































