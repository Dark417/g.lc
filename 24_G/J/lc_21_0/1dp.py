# dp


# 509. Fibonacci Number 斐波那契数
def fib(self, n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a % 1000000007


# 70. 爬楼梯
def climbStairs(self, n: int) -> int:
    a, b = 1, 1
    for i in range(1, n):
        a, b = b, a + b
    return b


# 1137. 第 N 个泰波那契数
def tribonacci(self, n: int) -> int:
        a, b, c = 0, 0, 1
    for i in range(n):
        a, b, c = b, c, a+b+c
    return b



# 206.746. Min Cost Climbing Stairs 使用最小花费爬楼梯
def minCostClimbingStairs(self, cost: List[int]) -> int:
    a = b = 0
    for c in cost:
        a, b = b, c + min(a, b)
    return min(a, b)


# 面试题 16.11. 跳水板

def divingBoard(self, shorter: int, longer: int, k: int) -> List[int]:
    if not k:
        return []
    if shorter == longer:
        return [shorter * k]
    res = [0] * (k + 1)
    for i in range(k + 1):
        res[i] = shorter * (k - i) + longer * i
    return res














































































































