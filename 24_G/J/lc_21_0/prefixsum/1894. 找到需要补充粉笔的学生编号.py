# 1894. 找到需要补充粉笔的学生编号

def chalkReplacer(self, chalk: List[int], k: int) -> int:
    sm = sum(chalk)
    rm = k % sm
    for i in range(len(chalk)):
        rm -= chalk[i]
        if rm < 0:
            return i
    # return -1


def chalkReplacer(self, chalk: List[int], k: int) -> int:
    total = sum(chalk)
    k %= total
    res = -1
    for i, cnt in enumerate(chalk):
        if cnt > k:
            res = i
            break
        k -= cnt
    return res



def chalkReplacer(self, chalk: List[int], k: int) -> int:
    n = len(chalk)
    if chalk[0] > k:
        return 0
    for i in range(1, n):
        chalk[i] += chalk[i - 1]
        if chalk[i] > k:
            return i

    k %= chalk[-1]
    return bisect_right(chalk, k)




def chalkReplacer(self, chalk: List[int], k: int) -> int:
    n = len(chalk)
    sums, presum = 0, []
    for i in range(n):
        sums += chalk[i]
        presum.append(sums)
    k %= sums
    l, r = 0, n - 1
    while l < r - 1:
        mid = (l + r) >> 1
        if presum[mid] <= k:
            l = mid
        else:
            r = mid
    return l if presum[l] > k else r


















