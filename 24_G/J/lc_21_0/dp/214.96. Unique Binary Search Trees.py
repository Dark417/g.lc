"""
214.96. Unique Binary Search Trees
不同的二叉搜索树

Given n, how many structurally unique BST's (binary search trees) that store values 1 ... n?

Example:

Input: 3
Output: 5
Explanation:
Given n = 3, there are a total of 5 unique BST's:

   1         3     3      2      1
    \       /     /      / \      \
     3     2     1      1   3      2
    /     /       \                 \
   2     1         2                 3
 

Constraints:

1 <= n <= 19
"""





def numTrees(self, n):
    G = [0]*(n+1)
    G[0], G[1] = 1, 1

    for i in range(2, n+1):
        for j in range(1, i+1):
            G[i] += G[j-1] * G[i-j]

    return G[n]



def numTrees(self, n):
    C = 1
    for i in range(0, n):
        C = C * 2*(2*i+1)/(i+2)
    return int(C)


# caikehe
# DP
def numTrees1(self, n):
    res = [0] * (n+1)
    res[0] = 1
    for i in xrange(1, n+1):
        for j in xrange(i):
            res[i] += res[j] * res[i-1-j]
    return res[n]


# Catalan Number  (2n)!/((n+1)!*n!)  
def numTrees(self, n):
    return math.factorial(2*n)/(math.factorial(n)*math.factorial(n+1))






def numTrees(self, n: int) -> int:
    if n <= 1:
        return 1
    res = 0
    for i in range(1, n + 1):
        res += self.numTrees(i - 1) * self.numTrees(n - i)
    return res



visited = dict()

def numTrees(self, n: int) -> int:
    if n in self.visited:
        return self.visited.get(n)
    if n <= 1:
        return 1
    res = 0
    for i in range(1, n + 1):
        res += self.numTrees(i - 1) * self.numTrees(n - i)
    self.visited[n] = res
    return res



from functools import lru_cache

@lru_cache()
def numTrees(self, n: int) -> int:
    if n <= 0: return 1
    if n <= 2: return n

    return sum([self.numTrees(i-1) * self.numTrees(n-i) for i in range(1, n + 1)])




def numTrees(self, n: int) -> int:
    store = [1,1] #f(0),f(1)
    if n <= 1:
        return store[n]
    for m in range(2,n+1):
        s = m-1
        count = 0
        for i in range(m):
            count += store[i]*store[s-i]
        store.append(count)
    return store[n]


def numTrees(self, n: int) -> int:
    a=[1]
    for j in range(n):
        c=0
        temp=a.copy()
        temp.reverse()
        for i in range(len(a)):
            c+=a[i]*temp[i]
        a.append(c)
    return a[-1]
























































