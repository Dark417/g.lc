# 131. 分割回文串

# basic
def partition(self, s: str) -> List[List[str]]:
    res = []
    def helper(s, tmp):
        if not s:
            res.append(tmp)
        for i in range(1, len(s) + 1):
            if s[:i] == s[:i][::-1]:
                helper(s[i:], tmp + [s[:i]])
    helper(s, [])
    return res


# dp
def partition(self, s: str) -> List[List[str]]:
    n = len(s)
    dp = [[False] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1):
            if (s[i] == s[j]) and (i - j <= 2 or dp[j + 1][i - 1]):
                dp[j][i] = True
    res = []

    def helper(i, tmp):
        if i == n:
            res.append(tmp)
        for j in range(i, n):
            if dp[i][j]:
                helper(j + 1, tmp + [s[i: j + 1]])

    helper(0, [])
    return res




# basic +
def partition(self, s: str) -> List[List[str]]:
    if not s:
        return [[]]
    if len(s) == 1:
        return [[s]]
    ret = []
    for i in range(1, len(s)+1):
        if s[:i][::-1] == s[:i]:
            ret += [[s[:i]]+j for j in self.partition(s[i:])]
    return ret






# 中心扩散
def partition(self, s: str) -> List[List[str]]:
    def centerSpread(left, right):
        while 0 <= left and right < size and s[left] == s[right]:
            dp[left][right] = True
            left -= 1
            right += 1
    
    def recall(s, size, start, subset):
        if start == size:
            res.append(subset[:])
            return 
        for i in range(start, size):
            if not dp[start][i]:
                continue
            subset.append(s[start:i+1])
            recall(s, size, i+1, subset)
            subset.pop()

    res = []
    size = len(s)
    dp = [[False for _ in range(size)] for _ in range(size)]
    for i in range(size):
        centerSpread(i, i)
        centerSpread(i, i+1)

    recall(s, size, 0, [])
    return res




# 中心扩散
def partition(self, s: str) -> List[List[str]]:
    if not s:
        return []
    n = len(s)
    is_palin = [[False]*n for _ in range(n)]
    for c in range(n):
        i, j = c, c 
        while 0<=i and j<n and s[i]==s[j]:
            is_palin[i][j] = True
            i -= 1
            j += 1
    for c in range(n-1):
        i, j = c, c+1 
        while 0<=i and j<n and s[i]==s[j]:
            is_palin[i][j] = True
            i -= 1
            j += 1
    
    self.res = []
    def dfs(ss, tmp, t):
        if not ss:
            self.res.append(tmp[:])
            return 
        for i in range(t, n):
            if is_palin[t][i]:
                tmp.append(s[t:i+1])
                dfs(s[i+1:] ,tmp, i+1)
                tmp.pop()

    dfs(s, [], 0)
    return self.res 





# ???
def partition(self, s: str) -> List[List[str]]:
    if s == "":
        return []
    ans = [[s[0]] ]
    for i in range(1, len(s)):
        curr = s[i]
        newAns = []
        for item in ans:
            newAns.append(item + [curr])
            if item[-1] == curr:
                newAns.append(item[0:-1] + [item[-1] + curr])
            if len(item) >= 2 and item[-2] == curr:
                newAns.append(item[0:-2] + [item[-2] + item[-1] + curr])
        ans = newAns 
    return ans




def partition(self, s: str) -> List[List[str]]:
    dp = [[] for _ in range(len(s) + 1)]
    dp[-1] = [[]]
    for i in range(len(s) - 1, -1, -1):
        for j in range(i + 1, len(s) + 1):
            if s[i:j] == s[i:j][::-1]:
                for each in dp[j]:
                    dp[i].append([s[i:j]] + each)
    return dp[0]









def partition(self, s: str) -> List[List[str]]:
    res = []
    if not s: return res

    def backtrack(lastStr, paths):
        if len(lastStr) == 0:  # 如果字符串没有了，就代表分割完了
            res.append(paths[:])
            return

        for i in range(len(lastStr)):
            first = lastStr[:i + 1]  # a
            last = lastStr[i + 1:]  # 剩余的字符串 ab

            if not self.isPalindrome(first): continue

            paths.append(first)
            backtrack(last,paths)
            paths.pop()

    backtrack(s,[])
    return res
    
def isPalindrome(self, s):
    i, j = 0, len(s)-1
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1

    return True




def partition(self, s: str) -> List[List[str]]:
    if not s:
        return []
    if len(s) == 1:
        return [[s]]

    m = len(s)
    result = []
    dp = [[0 for i in range(m)] for i in range(m)]  # dp数组在这里记载的是，[i,j]双闭区间能否构成回文串。（1）若能构成，则dp[i,j]则为回文串长度。（2）若不能，dp[i,j]则为0

    for j in range(0, m):
        for i in range(0, j+1):
            if s[i] == s[j]:
                if j-i < 3 or dp[i+1][j-1] > 0:
                    dp[i][j] = j-i+1
                else:
                    dp[i][j] = 0
            else:
                dp[i][j] = 0

    def dfs_helper(i, temp):  # 深度优先遍历，对于当前的位置i，看一下[i,j]能否构成回文串，若能，则继续深度优先遍历，到达极限则记录结果。记得回溯
        nonlocal dp, result, s
        if i == len(dp):
            result.append(temp.copy())

        for j in range(i, len(dp)):
            if dp[i][j]:
                temp.append(s[i:j+1])
                dfs_helper(j+1, temp)
                temp.pop()

    temp_result = []
    dfs_helper(0, temp_result)
    return result












