"""
213.256. Paint House
粉刷房子

假如有一排房子，共 n 个，每个房子可以被粉刷成红色、蓝色或者绿色这三种颜色中的一种，你需要粉刷所有的
房子并且使其相邻的两个房子颜色不能相同。

当然，因为市场上不同颜色油漆的价格不同，所以房子粉刷成不同颜色的花费成本也是不同的。每个房子粉刷成不
颜色的花费是以一个 n x 3 的矩阵来表示的。

例如，costs[0][0] 表示第 0 号房子粉刷成红色的成本花费；costs[1][2] 表示第 1 号房子粉刷成绿色的
费，以此类推。请你计算出粉刷完所有房子最少的花费成本。

注意：

所有花费均为正整数。

示例：

输入: [[17,2,17],[16,16,5],[14,3,19]]
输出: 10
解释: 将 0 号房子粉刷成蓝色，1 号房子粉刷成绿色，2 号房子粉刷成蓝色。
     最少花费: 2 + 5 + 3 = 10。

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/paint-house
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。


"""

def minCost(self, costs: List[List[int]]) -> int:
    for i in range(1, len(costs)):
        costs[i][0] = costs[i][0] + min(costs[i-1][1], costs[i-1][2])
        costs[i][1] = costs[i][1] + min(costs[i-1][0], costs[i-1][2])
        costs[i][2] = costs[i][2] + min(costs[i-1][0], costs[i-1][1])
    return min(costs[-1]) if costs else 0



def minCost(self, costs: List[List[int]]) -> int:
    for i in range(1, len(costs)):
        for j in range(3):
            costs[i][j] = costs[i][j] + min(costs[i-1][(j+1)%3], costs[i-1][(j+2)%3])
    return min(costs[-1]) if costs else 0


def minCost(self, costs: List[List[int]]) -> int:
    for i in range(len(costs)-2,-1,-1):
        for k in range(3):
            costs[i][k] = min(costs[i][k]+costs[i+1][(k+1)%3],costs[i][k]+costs[i+1][(k+2)%3])
    return min(costs[0]) if costs else 0



def minCost(self, costs: List[List[int]]) -> int:
    def rec(l, i):
        c = costs[l][i]
        if (l, i) in memo:
        	return memo[(l, i)]
        if l != len(costs) - 1:
            c += min(rec(l+1, (i+1)%3), rec(l+1, (i+2)%3))
        memo[(l,i)] = c
        return c
    memo = {}
    return min(rec(0, 0), rec(0, 1), rec(0, 2)) if len(costs) else 0



def minCost(self, costs: List[List[int]]) -> int:
    def rec(l, i):
        c = costs[l][i]
        if l != len(costs) - 1:
            c += min(rec(l+1, (i+1)%3), rec(l+1, (i+2)%3))
        return c
    return min(rec(0, 0), rec(0, 1), rec(0, 2)) if len(costs) else 0



def minCost(self, costs):
	def paint_cost(n, color):
        total_cost = costs[n][color]
        if n == len(costs) - 1:
            pass
        elif color == 0: # Red
            total_cost += min(paint_cost(n + 1, 1), paint_cost(n + 1, 2))
        elif color == 1: # Green
            total_cost += min(paint_cost(n + 1, 0), paint_cost(n + 1, 2))
        else: # Blue
            total_cost += min(paint_cost(n + 1, 0), paint_cost(n + 1, 1))
        return total_cost

	if costs == []:
	    return 0
	return min(paint_cost(0, 0), paint_cost(0, 1), paint_cost(0, 2))






































































