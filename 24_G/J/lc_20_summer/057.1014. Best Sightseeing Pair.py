"""
057.1014. Best Sightseeing Pair
最佳观光组合

Given an array A of positive integers, A[i] represents the value of the i-th 
sightseeing spot, and two sightseeing spots i and j have distance j - i between them.

The score of a pair (i < j) of sightseeing spots is (A[i] + A[j] + i - j): 
the sum of the values of the sightseeing spots, minus the distance between them.

Return the maximum score of a pair of sightseeing spots.

 

Example 1:

Input: [8,1,5,2,6]
Output: 11
Explanation: i = 0, j = 2, A[i] + A[j] + i - j = 8 + 5 + 0 - 2 = 11
 

Note:

2 <= A.length <= 50000
1 <= A[i] <= 1000


a[i] + a[j] + i - j可以这么看 (a[i] + i) + （a[j] - j）


"""




def maxScoreSightseeingPair(self, A):
    return reduce(lambda (r, c), a: [max(r, c + a), max(c, a) - 1], A, [0, 0])[0]


def maxScoreSightseeingPair(self, A):
    cur = res = 0
    for a in A:
        res = max(res, cur + a)
        cur = max(cur, a) - 1
    return res


def maxScoreSightseeingPair(self, A: [int]) -> int:
    length = len(A)
    if length == 0: return 0
    if length == 1: return A[0]

    dp = A[0]*2     # 存储以当前景点结尾的最佳评分
    max_score =0    # 存储历史最佳评分
    for i in range(1, length):
        dp = max(dp - A[i-1] + A[i] -1, A[i-1] + A[i] -1)
        max_score = max(max_score, dp)
    return max_score

    dp[i] = max(dp[i-1]-1,A[i])


def maxScoreSightseeingPair(self, a: List[int]) -> int:
    max_so_far,result = a[0],0
    for i in range(1,len(a)):
        result = max(result, max_so_far + a[i] - i)
        max_so_far = max(max_so_far, a[i] + i)
    return result


def maxScoreSightseeingPair(self, A: List[int]) -> int:
    best_i = 0
    res = 0
    for i, v in enumerate(A):
        # here v - i is actually `A[j] - j` in the formula
        res = max(res, v - i + best_i)
        # here we store `A[i] + i`
        best_i = max(best_i, v + i)
    return res


	for j in range(1, len(A)):
		res = max(res, pre_max + A[j] - j) #判断能否刷新res
		pre_max = max(pre_max, A[j] + j) #判断能否刷新pre_max， 得到更大的A[i] + i
     



"""
int ans = 0, mx = A[0] + 0;
for (int j = 1; j < A.size(); ++j) {
    ans = max(ans, mx + A[j] - j);
    // 边遍历边维护
    mx = max(mx, A[j] + j);
}

	


"""

def maxScoreSightseeingPair(self, A: List[int]) -> int:
    res = cur = 0
    i = 0
    for j in range(len(A)):
        res = max(res, cur+A[j]+i-j)
        print(res)
        if cur+i -j < A[j]:
            cur = A[j]
            i = j
    return res





def maxScoreSightseeingPair(self, A: List[int]) -> int:
	score = 0
	for i in range(len(A)-1):
		for j in range(i+1, len(A)):
			score = max(score, A[i]+A[j]+i-1)
	return score


def maxScoreSightseeingPair(self, A: List[int]) -> int:
    score = 0
    def dp(i,j):
        if j - i == 1:
            return A[i] + A[j] + i - j
        else:
            return max(A[i] + A[j] + i - j, dp(i+1, j), dp(i, j-1))

    score = dp(0, len(A)-1)
    return score








































