"""
249.279. Perfect Squares
完全平方数



Given a positive integer n, find the least number of perfect square numbers (for example, 1, 4, 9, 16, ...) which sum to n.

Example 1:

Input: n = 12
Output: 3 
Explanation: 12 = 4 + 4 + 4.
Example 2:

Input: n = 13
Output: 2
Explanation: 13 = 4 + 9.


"""



# Stefan
class Solution(object):
    _dp = [0]
    def numSquares(self, n):
        dp = self._dp
        while len(dp) <= n:
            dp += min(dp[-i*i] for i in range(1, int(len(dp)**0.5+1))) + 1,
        return dp[n]





def numSquares(self, n: int) -> int:
    dp=[i for i in range(n+1)]
    for i in range(2,n+1):
        for j in range(1,int(i**(0.5))+1):
            dp[i]=min(dp[i],dp[i-j*j]+1)
    return dp[-1]




 
def numSquares(self, n: int) -> int:
    square_nums = [i**2 for i in range(1, int(math.sqrt(n))+1)]

    def minNumSquares(k):
        print("k ", k)
        """ recursive solution """
        # bottom cases: find a square number
        if k in square_nums:
            return 1
        min_num = float('inf')

        # Find the minimal value among all possible solutions
        for square in square_nums:
            print("sqr ", square)
            if k < square:
                break
            new_num = minNumSquares(k-square) + 1
            min_num = min(min_num, new_num)
        return min_num

    return minNumSquares(n)










def numSquares(self, n: int) -> int:
    from collections import deque
    deq=deque()
    visited=set()
    
    deq.append((n,0))
    while deq:
        number,step=deq.popleft()
        targets=[number-i*i for i in range(1,int(number**0.5)+1)]
        for target in targets:
            if target==0:return step+1
            if target not in visited:
                deq.append((target,step+1))
                visited.add(target)
    return 0




def numSquares(self, n: int) -> int:
    from collections import deque
    if n == 0: return 0
    queue = deque([n])
    step = 0
    visited = set()
    while(queue):
        step+=1
        l=len(queue)
        for _ in range(l):
            tmp=queue.pop()
            for i in range(1,int(tmp**0.5)+1):
                x=tmp-i**2
                if(x==0):
                    return step
                if(x not in visited):
                    queue.appendleft(x)
                    visited.add(x)
    return step


















































































