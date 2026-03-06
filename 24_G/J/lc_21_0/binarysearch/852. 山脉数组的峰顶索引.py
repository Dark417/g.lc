# 852. 山脉数组的峰顶索引


def peakIndexInMountainArray(self, A):
    lo, hi = 0, len(A) - 1
    while lo < hi:
        mi = (lo + hi) / 2
        if A[mi] < A[mi + 1]:
            lo = mi + 1
        else:
            hi = mi
    return lo

# l < r, 退出条件 l = r = 违反条件的第一个