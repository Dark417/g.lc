# 5. 最长回文子串

def longestPalindrome(self, s: str) -> str:
    n = len(s)
    if n < 2:
        return s
    
    max_len = 1
    begin = 0
    dp = [[False] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = True
    
    for L in range(2, n + 1):
        # 枚举左边界，左边界的上限设置可以宽松一些
        for i in range(n):
            # 由 L 和 i 可以确定右边界，即 j - i + 1 = L 得
            j = L + i - 1
            # 如果右边界越界，就可以退出当前循环
            if j >= n:
                break
                
            if s[i] != s[j]:
                dp[i][j] = False 
            else:
                if j - i < 3:
                    dp[i][j] = True
                else:
                    dp[i][j] = dp[i + 1][j - 1]
            
            # 只要 dp[i][L] == true 成立，就表示子串 s[i..L] 是回文，此时记录回文长度和起始位置
            if dp[i][j] and j - i + 1 > max_len:
                max_len = j - i + 1
                begin = i
    return s[begin:begin + max_len]





def expandAroundCenter(self, s, left, right):
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return left + 1, right - 1

def longestPalindrome(self, s: str) -> str:
    start, end = 0, 0
    for i in range(len(s)):
        left1, right1 = self.expandAroundCenter(s, i, i)
        left2, right2 = self.expandAroundCenter(s, i, i + 1)
        if right1 - left1 > end - start:
            start, end = left1, right1
        if right2 - left2 > end - start:
            start, end = left2, right2
    return s[start: end + 1]






def longestPalindrome(self, s: str) -> str:
    if len(s) <= 1:
        return s

    n = len(s)
    mat = [[1] * n] + [[0] * n for _ in range(n-1)]
    
    def checkpa(start, end):
        if end - start + 1 <= 1:
            return True
        elif s[start] == s[end]:
            if mat[start+1][end-1] == 1:
                mat[start][end] == 1
                return True
            else:
                return False
        else:
            return False

    leng = 2
    res = (0, 1)
    ms = 1
    ansleng = 0
    while leng <= n:
        for i in range(n):
            if i + leng <= n:
                if checkpa(i, i + leng-1):
                    if leng > ms and leng > ansleng:
                        res = (i, i + leng)
                        print(res)
                        ansleng = leng
        leng += 1
    print(mat)
    return s[res[0]: res[1]] if leng > 1 else s[0]









