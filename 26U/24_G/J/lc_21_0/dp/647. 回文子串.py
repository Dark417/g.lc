# 647. 回文子串




def countSubstrings(self, s: str) -> int:
    dp = [[False for _ in range(len(s))] for _ in range(len(s))]
    ans = 0

    for j in range(len(s)):
        for i in range(j+1):
            if s[i] == s[j] and (j-i<2 or dp[i+1][j-1]):
                dp[i][j] = True
                ans += 1
    return ans



def countSubstrings(self, s: str) -> int:
    dp = [[False] * len(s) for _ in range(len(s))]
    result = 0
    for i in range(len(s)-1, -1, -1): #注意遍历顺序
        for j in range(i, len(s)):
            if s[i] == s[j] and (j - i <= 1 or dp[i+1][j-1]): 
                result += 1
                dp[i][j] = True
    return result




def countSubstrings(self, s: str) -> int:
    result = 0
    for i in range(len(s)):
        result += self.extend(s, i, i, len(s)) #以i为中心
        result += self.extend(s, i, i+1, len(s)) #以i和i+1为中心
    return result

def extend(self, s, i, j, n):
    res = 0
    while i >= 0 and j < n and s[i] == s[j]:
        i -= 1
        j += 1
        res += 1
    return res



def countSubstrings(self, s: str) -> int:
    ans = 0
    if not s: return ans
    for i in range(len(s)):
        cnt1 = self.expandAndCount(s, i, i) # 中心点为一个字母
        cnt2 = self.expandAndCount(s, i, i+1) # 中心点为两个字母
        ans = ans + cnt1 + cnt2
    return ans

def expandAndCount(self, s, begin, end) -> int:
    cnt = 0
    while begin >=0 and end < len(s) and s[begin] == s[end]:
        cnt += 1
        begin -= 1
        end += 1
    return cnt



def countSubstrings(self, s: str) -> int:
    n,ans = len(s),0
    for i in range(2*n-1):
        l,r = i//2,i//2+i%2
        while l >= 0 and r < n and s[l]==s[r]:
            ans += 1
            l -= 1
            r += 1
    return ans





def countSubstrings(self, s: str) -> int:
    n = len(s)
    if n == 1:
        return 1

    dp = [[0] * n for _ in range(n)]
    # dp = [[False for _ in range(len(s))] for _ in range(len(s))]
    for i in range(n):
        dp[i][i] = 1

    for j in range(n):
        for i in range(j+1):
            print(i,j)
            if s[i] == s[j] and (dp[i+1][j-1]>0 or j-i<2):
                dp[i][j] += 1
            
            print(dp)
    return dp[-1][-1]





















