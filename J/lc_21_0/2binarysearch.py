




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


# 1064. 不动点
# bug!
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




# mid
# 287. 寻找重复数

def findDuplicate(self, nums: List[int]) -> int:
    size = len(nums)
    left = 1
    right = size - 1

    while left < right:
        mid = left + (right - left) // 2

        cnt = 0
        for num in nums:
            if num <= mid:
                cnt += 1
        if cnt > mid:
            right = mid
        else:
            left = mid + 1
    return left











# 74. 搜索二维矩阵
def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
    for m in range(len(matrix)):
        if matrix[m][0] <= target and matrix[m][-1] >= target:
            l, r = 0, len(matrix[0]) - 1
            while l <= r:
                mid = l + (r - l) // 2
                if matrix[m][mid] == target:
                    return True
                elif matrix[m][mid] < target:
                    l = mid + 1
                else:
                    r = mid - 1
    return False


























































