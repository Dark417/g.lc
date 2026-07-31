"""
226.265. Paint House II
粉刷房子 III


假如有一排房子，共 n 个，每个房子可以被粉刷成 k 种颜色中的一种，你需要粉刷所有的房子并且使其相邻的两个房子颜色不能相同。

当然，因为市场上不同颜色油漆的价格不同，所以房子粉刷成不同颜色的花费成本也是不同的。每个房子粉刷成不同颜色的花费是以一个 n x k 的矩阵来表示的。

例如，costs[0][0] 表示第 0 号房子粉刷成 0 号颜色的成本花费；costs[1][2] 表示第 1 号房子粉刷成 2 号颜色的成本花费，以此类推。请你计算出粉刷完所有房子最少的花费成本。

注意：

所有花费均为正整数。

示例：

输入: [[1,5,3],[2,9,4]]
输出: 5
解释: 将 0 号房子粉刷成 0 号颜色，1 号房子粉刷成 2 号颜色。最少花费: 1 + 4 = 5; 
     或者将 0 号房子粉刷成 2 号颜色，1 号房子粉刷成 0 号颜色。最少花费: 3 + 2 = 5. 
进阶：
您能否在 O(nk) 的时间复杂度下解决此问题？

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/paint-house-ii
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

sys.maxsize
"""

def minCostII(self, costs: List[List[int]]) -> int:
    def rec(l, i):
        c = costs[l][i]
        n = len(costs[0])
        if (l, i) in memo:
            return memo[(l, i)]
        if l != len(costs) - 1:
            c += min(rec(l+1, (i+k+1)%n) for k in range(n-1))
        memo[(l,i)] = c
        return c
    memo = {}
    return min(rec(0, i) for i in range(len(costs[0]))) if costs else 0



def minCostII(self, costs: List[List[int]]) -> int:
    if not costs: return 0
    n = len(costs[0])
    for i in range(1, len(costs)):
        for k in range(n):
            costs[i][k] = min(costs[i][k] + costs[i-1][j%n] for j in range(k+1, k+n))
    return min(costs[-1])



def minCostII(self, costs: List[List[int]]) -> int:
    if not costs: return 0  # 特判
    for i in range(1, len(costs)):
        for j in range(len(costs[0])):
            costs[i][j] += min(costs[i-1][:j] + costs[i-1][j+1:])  # 切片+拼接, list + list = list, 略去元素costs[i-1][j]
    return min(costs[-1])






def minCostII(self, costs: List[List[int]]) -> int:
    if not costs:
        return 0
    dp = costs.copy()
    k = len(costs[0])
    def smallest2(arr):
        min1 = [-1, float('inf')]
        min2 = [-1, float('inf')]
        for i, num in enumerate(arr):
            if num < min1[1]:
                min2 = min1.copy()
                min1 = [i, num]
            elif num < min2[1]:
                min2 = [i, num]
        return min1, min2
    for i in range(1, len(costs)):
        min1, min2 = smallest2(dp[i-1])
        dp[i] = [cost + min1[1] for cost in dp[i]]
        dp[i][min1[0]] += min2[1] - min1[1]
    return min(dp[-1])







def minCostII(self, costs: List[List[int]]) -> int:
    if not costs:
        return 0
    dp=costs
    n=len(dp)
    k=len(dp[0])
    for i in range(1,n):    
        for x in range(0,k):
            minp=inf
            for j in range(0,k):
                if j==x:
                    continue
                minp=min(dp[i-1][j],minp)
            dp[i][x]+=minp
    return min(dp[-1])




def minCostII(self, costs: List[List[int]]) -> int:
    if not costs or not costs[0]: return 0

    n, k = len(costs), len(costs[0])

    dp = [[sys.maxsize for _ in range(k)] for _ in range(n)]
    dp[0] = costs[0]

    for i in range(1, n):  # 1
        for j in range(k):  # 2
            for t in range(k):  # 3
                if t == j: continue
                dp[i][j] = min(dp[i][j], dp[i - 1][t])
            dp[i][j] += costs[i][j]

    return min(dp[n - 1])



def minCostII(self, costs: List[List[int]]) -> int:
    if not costs or not costs[0]: return 0
    n, k = len(costs), len(costs[0])
    first, second, color = 0, 0, None

    for i in range(n):
        pfirst, psecond, pcolor = first, second, color  # 分别表示dp[i - 1]中的最小值，次小值，最小值颜色
        first, second, color = sys.maxsize, sys.maxsize, k  # 分别表示dp[i]中的最小值，次小值，最小值颜色，初始color设置一个不可能的值

        for j in range(k):
            curr = (pfirst if pcolor != j else psecond) + costs[i][j]  # dp[i][j] = dp[i - 1]中的最小值，如果最小值颜色和j相同，那么就选次小值

            if curr < first: first, second, color = curr, first, j  # 更新当前的最小值、次小值等，用于下一轮
            elif curr < second: second = curr

    else: return min(first, second)


















