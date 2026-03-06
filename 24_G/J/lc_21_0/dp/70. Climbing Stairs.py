"""
204.70. Climbing Stairs
爬楼梯


You are climbing a stair case. It takes n steps to reach to the top.

Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

Example 1:

Input: 2
Output: 2
Explanation: There are two ways to climb to the top.
1. 1 step + 1 step
2. 2 steps
Example 2:

Input: 3
Output: 3
Explanation: There are three ways to climb to the top.
1. 1 step + 1 step + 1 step
2. 1 step + 2 steps
3. 2 steps + 1 step
 

Constraints:

1 <= n <= 45

https://leetcode-cn.com/problems/climbing-stairs/solution/pa-lou-ti-by-leetcode-solution/
"""

# 剑指 Offer 10- II. 青蛙跳台阶问题



def climbStairs(self, n: int) -> int:
    if n < 2: return n
    if n == 2: return 2
    l = [0, 1, 2] + [0] * (n-2)
    for i in range(3, n+1):
        l[i] = l[i-1] + l[i-2] 
    return l[n]


def climbStairs(self, n: int) -> int:
    a, b = 1, 1
    for i in range(1, n):
        a, b = b, a + b
    return b

def numWays(self, n: int) -> int:
        a, b = 1, 1
        for _ in range(n-1):
            a, b = b, a + b
        return b % 1000000007

def climbStairs(self, n):
    return self.climbStairs(n - 1) + self.climbStairs(n - 2) if n > 2 else n
        




def climbStairs(self, n: int) -> int:
    self.ttl = 0
    def dfs(cur):
        if cur > n: 
            return
        elif cur == n:
            self.ttl += 1
        else:
            for i in range(1, 3):
                dfs(cur+i)
    dfs(0)
    return self.ttl




def climbStairs(self, n: int) -> int:
	def dfs(i, n):
		if i > n:
			return 0
		if i == n:
			return 1
		return dfs(i + 1, n) + dfs(i + 2, n)
	return dfs(0, n)



def climbStairs(self, n: int) -> int:
	def rec(i, n, memo):
		if i > n:
			return 0
		if i == n:
			return 1
		if memo[i] > 0:
			return memo[i]
		memo[i] = rec(i+1, n, memo) + rec(i+2, n, memo)
		return memo[i]
	memo = [0] * (n+1)
	return rec(0, n, memo)





# caikehe
# Top down - TLE
def climbStairs1(self, n):
    if n == 1:
        return 1
    if n == 2:
        return 2
    return self.climbStairs(n-1)+self.climbStairs(n-2)
 
# Bottom up, O(n) space
def climbStairs2(self, n):
    if n == 1:
        return 1
    res = [0 for i in xrange(n)]
    res[0], res[1] = 1, 2
    for i in xrange(2, n):
        res[i] = res[i-1] + res[i-2]
    return res[-1]

# Bottom up, constant space
def climbStairs3(self, n):
    if n == 1:
        return 1
    a, b = 1, 2
    for i in xrange(2, n):
        tmp = b
        b = a+b
        a = tmp
    return b
    
# Top down + memorization (list)
def climbStairs4(self, n):
    if n == 1:
        return 1
    dic = [-1 for i in xrange(n)]
    dic[0], dic[1] = 1, 2
    return self.helper(n-1, dic)
    
def helper(self, n, dic):
    if dic[n] < 0:
        dic[n] = self.helper(n-1, dic)+self.helper(n-2, dic)
    return dic[n]
    
# Top down + memorization (dictionary)  
def __init__(self):
    self.dic = {1:1, 2:2}
    
def climbStairs(self, n):
    if n not in self.dic:
        self.dic[n] = self.climbStairs(n-1) + self.climbStairs(n-2)
    return self.dic[n]


















# Top down - TLE
def climbStairs1(self, n):
    if n == 1:
        return 1
    if n == 2:
        return 2
    return self.climbStairs(n-1)+self.climbStairs(n-2)
 
# Bottom up, O(n) space
def climbStairs2(self, n):
    if n == 1:
        return 1
    res = [0 for i in xrange(n)]
    res[0], res[1] = 1, 2
    for i in xrange(2, n):
        res[i] = res[i-1] + res[i-2]
    return res[-1]

# Bottom up, constant space
def climbStairs3(self, n):
    if n == 1:
        return 1
    a, b = 1, 2
    for i in xrange(2, n):
        tmp = b
        b = a+b
        a = tmp
    return b
    
# Top down + memorization (list)
def climbStairs4(self, n):
    if n == 1:
        return 1
    dic = [-1 for i in xrange(n)]
    dic[0], dic[1] = 1, 2
    return self.helper(n-1, dic)
    
def helper(self, n, dic):
    if dic[n] < 0:
        dic[n] = self.helper(n-1, dic)+self.helper(n-2, dic)
    return dic[n]
    
# Top down + memorization (dictionary)  
def __init__(self):
    self.dic = {1:1, 2:2}
    
def climbStairs(self, n):
    if n not in self.dic:
        self.dic[n] = self.climbStairs(n-1) + self.climbStairs(n-2)
    return self.dic[n]
































