# 525. 连续数组

def findMaxLength(self, nums: List[int]) -> int:
    res = 0
    n = len(nums)
    cur = 0
    hsh = {0: -1}
    for i in range(n):
        if nums[i] == 1:
            cur += 1
        else:
            cur -= 1
        if cur in hsh:
            res = max(res, i - hsh[cur])
        else:
            hsh[cur] = i
    return res


def findMaxLength(self, nums: List[int]) -> int:
    res = 0
    n = len(nums)
    xnums = [i if i == 1 else -1 for i in nums]
    for i in range(1, n):
        xnums[i] = xnums[i-1] + xnums[i]
    hsh = {0: -1}
    for i in range(n):
        if xnums[i] in hsh:
            res = max(res, i - hsh[xnums[i]])
        else:
            hsh[xnums[i]] = i
    return res




















