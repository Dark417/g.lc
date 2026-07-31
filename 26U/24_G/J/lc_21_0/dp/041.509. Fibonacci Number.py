"""
041.509. Fibonacci Number
斐波那契数

The Fibonacci numbers, commonly denoted F(n) form a sequence, 
called the Fibonacci sequence, such that each number is the sum of 
the two preceding ones, starting from 0 and 1. That is,

F(0) = 0,   F(1) = 1
F(N) = F(N - 1) + F(N - 2), for N > 1.
Given N, calculate F(N).

 

Example 1:

Input: 2
Output: 1
Explanation: F(2) = F(1) + F(0) = 1 + 0 = 1.
Example 2:

Input: 3
Output: 2
Explanation: F(3) = F(2) + F(1) = 1 + 1 = 2.
Example 3:

Input: 4
Output: 3
Explanation: F(4) = F(3) + F(2) = 2 + 1 = 3.
 

Note:

0 ≤ N ≤ 30.

"""


def fib(self, n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a % 1000000007


def fib(self, n: int) -> int:
        if n == 0: return 0
        if n == 1: return 1
        
        a, b, c = 0, 1, 2
        
        while c <= n:
            a, b = b, a + b
            c += 1
        return b % 1000000007



def fib(self, N: int) -> int:
    if N == 0: return 0
    if N == 1: return 1
    l = [0, 1]
    i = 2
    while i < (N+1):
        x = l[i-1] + l[i-2]
        l.append(x)
        i += 1
    return l.pop()


def fib(self, N: int) -> int:
    if N == 0: return 0
    if N == 1: return 1
    a, b = 0, 1
    i = 2
    while i < (N+1):
        a, b = b, (a+b)
        i += 1
    return b


def fib(self, N):           
	if N ==0 : return 0
	if N <=2 : return 1 
	temp1, temp2=1,1

	for i in range(3,N+1):
	 temp1, temp2 = temp2, temp1+temp2

	return temp2


def fib(self, N):
    a,b = 0,1
    for _ in range(N):
        a, b = b, a+b
    return a 

# lc 
def fib(N):
	if N == 0: return 0
	if N == 1: return 1
	return fib(N-1) + fib(N-2)

def fib(self, N: int) -> int:
        if N <= 1:
            return N
        return self.memoize(N)

    def memoize(self, N: int) -> {}:
        cache = {0: 0, 1: 1}

        # Since range is exclusive and we want to include N, we need to put N+1.
        for i in range(2, N+1):
            cache[i] = cache[i-1] + cache[i-2]

        return cache[N]


def fib(self, N: int) -> int:
        if N <= 1:
            return N
        self.cache = {0: 0, 1: 1}
        return self.memoize(N)

    def memoize(self, N: int) -> {}:
        if N in self.cache.keys():
            return self.cache[N]
        self.cache[N] = self.memoize(N-1) + self.memoize(N-2)
        return self.memoize(N)

def fib(self, N: int) -> int:
        if (N <= 1):
            return N
        if (N == 2):
            return 1

        current = 0
        prev1 = 1
        prev2 = 1

        # Since range is exclusive and we want to include N, we need to put N+1.
        for i in range(3, N+1):
            current = prev1 + prev2
            prev2 = prev1
            prev1 = current
        return current


def fib(self, N: int) -> int:
        if (N <= 1):
            return N

        A = [[1, 1], [1, 0]]
        self.matrix_power(A, N-1)

        return A[0][0]

    def matrix_power(self, A: list, N: int):
        if (N <= 1):
            return A

        self.matrix_power(A, N//2)
        self.multiply(A, A)
        B = [[1, 1], [1, 0]]

        if (N%2 != 0):
            self.multiply(A, B)

    def multiply(self, A: list, B: list):
        x = A[0][0] * B[0][0] + A[0][1] * B[1][0]
        y = A[0][0] * B[0][1] + A[0][1] * B[1][1]
        z = A[1][0] * B[0][0] + A[1][1] * B[1][0]
        w = A[1][0] * B[0][1] + A[1][1] * B[1][1]


def fib(self, N):
  	golden_ratio = (1 + 5 ** 0.5) / 2
  	return int((golden_ratio ** N + 1) / 5 ** 0.5)



def fib(self, N: int) -> int:
    	a, b = 0, 1
    	for i in range(N): a, b = b, a + b
    	return a



def fib(self, N: int) -> int:
    if N <= 1:
        return N
    return self.fib(N-1) + self.fib(N-2)



memo = {}
def fib(N):
	if N == 0: return 0
	if N == 1: return 1

	if N-1 not in memo: memo[N-1] = fib(N-1)
	if N-2 not in memo: memo[N-2] = fib(N-2)

	return memo[N-1] + memo[N-2]



from functools import lru_cache
class Solution:
    @lru_cache(maxsize=None)
    def fib(self, n: int) -> int:
        if n < 2: return n
        return self.fib(n-1) + self.fib(n-2)


def fib(N):
	if N == 0: return 0
	memo = [0,1]
	for _ in range(2,N+1):
		memo = [memo[-1], memo[-1] + memo[-2]]

	return memo[-1]


def fib(N):
	if N == 0: return 0
	memo = (0,1)
	for _ in range(2,N+1):
		memo = (memo[-1], memo[-1] + memo[-2])

	return memo[-1]


def fib(self, N):
	golden_ratio = (1 + 5 ** 0.5) / 2
	return int((golden_ratio ** N + 1) / 5 ** 0.5)


def fib(self, N):    
    fib_series =[0,1,1]
    
    if N <=2 : return fib_series[N]
    for i in range(3,N+1):
        fib_series.append(fib_series[i-1]+fib_series[i-2])
       
    return fib_series[N]
