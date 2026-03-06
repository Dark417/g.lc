# 40. 组合总和 II

def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
    def dfs(begin, path, residue):
        if residue == 0:
            res.append(path[:])
            return
        for index in range(begin, size):
            if candidates[index] > residue:
                break
            if index > begin and candidates[index - 1] == candidates[index]:
                continue
            path.append(candidates[index])
            dfs(index + 1, path, residue - candidates[index])
            path.pop()

    size = len(candidates)
    if size == 0:
        return []
    candidates.sort()
    res = []
    dfs(0, [], target)
    return res



def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
        def dfs(i, cur, target):
            if target == 0:
                res.append(cur)
                return
            if candidates[i] > target:
                return
            # if i < len(candidates) - 1 and candidates[i] == candidates[i + 1]:
            #     dfs(i + 2, cur, target)
            #     if target - candidates[i] >= 0:
            #         dfs(i + 2, cur + [candidates[i]], target - candidates[i])
            # else:
            dfs(i + 1, cur, target)
            if target - candidates[i] >= 0:
                dfs(i + 1, cur + [candidates[i]], target - candidates[i])

        res = []
        candidates.sort()
        dfs(0, [], target)
        return res



def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
    q = []
    n = len(candidates)
    if n == 0: return
    candidates.sort()
    for index, elem in enumerate(candidates):
        if elem > target:
            break
        if index == 0 or elem != candidates[index - 1]:
            q.append((elem, index, [elem]))
    res = []
    while len(q) > 0:
        sum, index, lst = q.pop(0)
        if sum == target:
            res.append(lst)
        elif sum < target:
            for i in range(index + 1, n):
                if sum + candidates[i] > target:
                    break
                if i == index + 1 or candidates[i] != candidates[i - 1]:
                    lst_new = lst.copy()
                    lst_new.append(candidates[i])
                    q.append((sum + candidates[i], i, lst_new))
    return res









def combinationSum2(self, candidates, target):
    candidates.sort()
    table = [None] + [set() for i in range(target)]
    for i in candidates:
        if i > target:
            break
        for j in range(target - i, 0, -1):
            table[i + j] |= {elt + (i,) for elt in table[j]}
        table[i].add((i,))
    return map(list, table[target])





def combinationSum2(self, candidates, target):
    candidates.sort()
    dp = [set() for i in xrange(target+1)]
    dp[0].add(())
    for num in candidates:
        for t in xrange(target, num-1, -1):
            for prev in dp[t-num]:
                dp[t].add(prev + (num,))
    return list(dp[-1])













