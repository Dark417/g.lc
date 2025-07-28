"""
180.986. Interval List Intersections
区间列表的交集

Given two lists of closed intervals, each list of intervals is pairwise disjoint and in sorted order.

Return the intersection of these two interval lists.

(Formally, a closed interval [a, b] (with a <= b) denotes the set of real numbers x with 
a <= x <= b.  The intersection of two closed intervals is a set of real numbers that is 
either empty, or can be represented as a closed interval.  For example, the intersection 
of [1, 3] and [2, 4] is [2, 3].)

 

Example 1:



Input: A = [[0,2],[5,10],[13,23],[24,25]], B = [[1,5],[8,12],[15,24],[25,26]]
Output: [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
 

Note:

0 <= A.length < 1000
0 <= B.length < 1000
0 <= A[i].start, A[i].end, B[i].start, B[i].end < 10^9


"""

def intervalIntersection(self, A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    i, j, res = 0, 0, []
    while i < len(A) and j < len(B):
        if A[i][0] <= B[j][0]:
            if A[i][1] <= B[j][1]:
                if A[i][1] < B[j][0]:
                    i += 1
                elif A[i][1] == B[j][0]:
                    res.append([A[i][1], A[i][1]])
                    i += 1
                else:
                    res.append([B[j][0], A[i][1]])
                    i += 1
            else:
                res.append([B[j][0], B[j][1]])
                j += 1
        else:
            if B[j][1] <= A[i][1]:
                if B[j][1] < A[i][0]:
                    j += 1
                elif B[j][1] == A[i][0]:
                    res.append([B[j][1], B[j][1]])
                    j += 1
                else:
                    res.append([A[i][0], B[j][1]])
                    j += 1
            else:
                res.append([A[i][0], A[i][1]])
                i += 1
    return res


def intervalIntersection(self, A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    i, j, res = 0, 0, []
    while i < len(A) and j < len(B):
        if A[i][0] <= B[j][0]:
            if A[i][1] <= B[j][1]:
                if A[i][1] > B[j][0]:
                    res.append([B[j][0], A[i][1]])
                elif A[i][1] == B[j][0]:
                    res.append([A[i][1], A[i][1]])
                i += 1
            else:
                res.append([B[j][0], B[j][1]])
                j += 1
        else:
            if B[j][1] <= A[i][1]:
                if B[j][1] > A[i][0]:
                    res.append([A[i][0], B[j][1]])
                elif B[j][1] == A[i][0]:
                    res.append([B[j][1], B[j][1]])
                j += 1
            else:
                res.append([A[i][0], A[i][1]])
                i += 1
    return res


def intervalIntersection(self, A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    i, j, res = 0, 0, []
    while i < len(A) and j < len(B):
        a, b = A[i], B[j]
        if a[0] <= b[0]:
            f, s = a, b
        else:
            f, s = b, a
        if f[1] <= s[1]:
            if f[1] == s[0]:
                res.append([f[1], f[1]])
            elif f[1] > s[0]:
                res.append([s[0], f[1]])
            if a[0] <= b[0]:
                i += 1
            else:
                j += 1
        else:
            res.append([s[0], s[1]])
            if a[0] <= b[0]:
                j += 1
            else:
                i += 1
    return res



# official
def intervalIntersection(self, A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    ans = []
    i = j = 0

    while i < len(A) and j < len(B):
        # Let's check if A[i] intersects B[j].
        # lo - the startpoint of the intersection
        # hi - the endpoint of the intersection
        lo = max(A[i][0], B[j][0])
        hi = min(A[i][1], B[j][1])
        if lo <= hi:
            ans.append([lo, hi])

        # Remove the interval with the smallest endpoint
        if A[i][1] < B[j][1]:
            i += 1
        else:
            j += 1

    return ans



def intervalIntersection(self, A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    m, n = len(A), len(B)
    i = j = 0
    res = []
    while i < m and j < n:
        if A[i][-1] >= B[j][0] and A[i][0] <= B[j][-1]:
            res.append([max(A[i][0], B[j][0]), min(A[i][-1], B[j][-1])])
        if A[i][-1] < B[j][-1]:
            i += 1
        else:
            j += 1
    return res 
































































































