"""
248.204. Count Primes
计数质数


Count the number of prime numbers less than a non-negative number, n.

Example:

Input: 10
Output: 4
Explanation: There are 4 prime numbers less than 10, they are 2, 3, 5, 7.


计数质数
"""



def count_primes_py(n):
    # 最小的质数是 2
    if n < 2:
        return 0

    isPrime = [1] * n
    isPrime[0] = isPrime[1] = 0   # 0和1不是质数，先排除掉

    # 埃式筛，把不大于根号n的所有质数的倍数剔除
    for i in range(2, int(n ** 0.5) + 1):
        if isPrime[i]:
            isPrime[i * i:n:i] = [0] * ((n - 1 - i * i) // i + 1)

    return sum(isPrime)



from numba import njit
import numpy as np

@njit
def count_primes_numpy_jit(n):
    assert n > 1

    isPrime = np.ones(n, dtype=np.bool_)
    isPrime[0] = isPrime[1] = 0

    for i in np.arange(2, int(n ** 0.5) + 1):
        if isPrime[i]:
            isPrime[i * i:n:i] = 0

    return int(np.sum(isPrime))



def countPrimes(self, n: int) -> int:
    res = 0
    for i in range(2, n):
        for j in range(2, i):
            if i % j == 0:
                break
        else:
            res += 1
    return res



def countPrimes(self, n: int) -> int:
    res = 0
    for i in range(2, n):
        for j in range(2, int(i ** 0.5) + 1):
            if i % j == 0:
                break
        else:
            res += 1
    return res



def countPrimes(self, n: int) -> int:
    isPrimes = [1] * n
    res = 0
    for i in range(2, n):
        if isPrimes[i] == 1: res += 1
        j = i
        while i * j < n:
            isPrimes[i * j] = 0
            j += 1
    return res



def countPrimes(self, n: int) -> int:
    if n < 2: return 0
	    isPrimes = [1] * n
	    isPrimes[0] = isPrimes[1] = 0
	    for i in range(2, int(n ** 0.5) + 1):
	        if isPrimes[i] == 1:
	            isPrimes[i * i: n: i] = [0] * len(isPrimes[i * i: n: i])
    return sum(isPrimes)



def countPrimes(self, n):
    if n <= 2:
        return 0
    res = [True] * n
    res[0] = res[1] = False
    for i in xrange(2, n):
        if res[i] == True:
            for j in xrange(2, (n-1)//i+1):
                res[i*j] = False
    return sum(res)










































