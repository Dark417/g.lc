"""
165.1304. Find N Unique Integers Sum up to Zero
和为零的N个唯一整数

Given an integer n, return any array containing n unique integers such that they add up to 0.

 

Example 1:

Input: n = 5
Output: [-7,-1,1,3,4]
Explanation: These arrays also are accepted [-5,-1,1,2,3] , [-3,-1,2,-2,4].
Example 2:

Input: n = 3
Output: [-1,0,1]
Example 3:

Input: n = 1
Output: [0]
 

Constraints:

1 <= n <= 1000



"""

def sumZero(self, n: int) -> List[int]:
    res = [ (-1)*i for i in range(n-1)]
    return res + [(-1)*sum(res)]


def sumZero(self, n):
    a = range(1, n)
    return a + [-sum(a)]


def sumZero(self, n):
    return range(1 - n, n, 2)



def sumZero(self, n):
	return [i for i in range((1 - n) // 2, n // 2 + 1) if i != 0 or n % 2 != 0]



def sumZero(self, n: int) -> List[int]:
    return list(range(-(n//2), 0)) + [0]*(n % 2) + list(range(1, n//2 + 1))

   
def sumZero(self, n: int) -> List[int]:
    return list(range(1,n))+[-n*(n-1)//2]



def sumZero(self, n):
	L, rem = n // 2, n % 2
		if rem != 0: ans = [0]
		else: ans = []
		for i in range(1,L+1):
		    ans.append(-i)
		    ans.append(i) 
		return ans









































































































































