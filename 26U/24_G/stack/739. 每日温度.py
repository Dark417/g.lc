# 739. 每日温度

def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
    n = len(temperatures)
    stack = []
    res = [0] * n

    for i in range(n):
        curt = temperatures[i]
        while stack and temperatures[stack[-1]]  < curt:
            preidx = stack.pop()
            res[preidx] = i - preidx
        stack.append(i)
    
    return res




def dailyTemperatures(self, T: List[int]) -> List[int]:
    n, right_max = len(T), float('-inf')
    res = [0] * n
    for i in range(n-1, -1, -1):
        t = T[i]
        if right_max <= t:
            right_max = t
        else:
            days = 1
            while T[i+days] <= t:
                days += res[i+days]
            res[i] = days
    return res







def dailyTemperatures(self, T):
    ans = [0] * len(T)
    stack = [] #indexes from hottest to coldest
    for i in xrange(len(T) - 1, -1, -1):
        while stack and T[i] >= T[stack[-1]]:
            stack.pop()
        if stack:
            ans[i] = stack[-1] - i
        stack.append(i)
    return ans





def dailyTemperatures(self, T: List[int]) -> List[int]:
    n = len(T)
    ans, nxt, big = [0] * n, dict(), 10**9
    for i in range(n - 1, -1, -1):
        warmer_index = min(nxt.get(t, big) for t in range(T[i] + 1, 102))
        if warmer_index != big:
            ans[i] = warmer_index - i
        nxt[T[i]] = i
    return ans






































