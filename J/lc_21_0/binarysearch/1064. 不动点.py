# 1064. 不动点


def fixedPoint(self, A: List[int]) -> int:
    left, right = 0, len(A)-1
    res = 10**9+1
    while left <= right:
        mid = (left+right)//2
        if A[mid] == mid:
            res = min(res, mid)
        if A[mid] >= mid:
            right = mid-1
        else:
            left = mid+1
    return res if res != 10**9+1 else -1





















