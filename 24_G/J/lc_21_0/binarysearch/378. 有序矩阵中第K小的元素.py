# 378. 有序矩阵中第K小的元素






def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
    x = []
    for r in matrix:
        x += r
    return sorted(x)[k-1]



def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
    rec = sorted(sum(matrix, []))
    return rec[k - 1]




def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
    n = len(matrix)
    pq = [(matrix[i][0], i, 0) for i in range(n)]
    heapq.heapify(pq)

    ret = 0
    for i in range(k - 1):
        num, x, y = heapq.heappop(pq)
        if y != n - 1:
            heapq.heappush(pq, (matrix[x][y + 1], x, y + 1))
    
    return heapq.heappop(pq)[0]



def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
    n = len(matrix)

    def check(mid):
        i, j = n - 1, 0
        num = 0
        while i >= 0 and j < n:
            if matrix[i][j] <= mid:
                num += i + 1
                j += 1
            else:
                i -= 1
        return num >= k

    left, right = matrix[0][0], matrix[-1][-1]
    while left < right:
        mid = (left + right) // 2
        if check(mid):
            right = mid
        else:
            left = mid + 1
    
    return left





def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
    l = matrix[0][0]
    r = matrix[-1][-1]
    
    while l < r:
        m = l + (r - l) // 2
        if sum(bisect.bisect(row, m) for row in matrix) < k:   # calculate how many numbers are on the left of middle number
            l = m + 1
        else:
            r = m
    return l






























