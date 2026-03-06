# 392. 判断子序列


def isSubsequence(self, s: str, t: str) -> bool:  
    from collections import defaultdict
    import bisect
    lookup = defaultdict(list)
    for idx, val in enumerate(t):
        lookup[val].append(idx)
    loc = -1
    for a in s:
        j = bisect.bisect_left(lookup[a], loc + 1)
        if j >= len(lookup[a]): return False
        loc = lookup[a][j]
    return True


def isSubsequence(self, s, t):
    t = iter(t)
    return all(i in t for i in s) 


def isSubsequence(self, s: str, t: str) -> bool:
    n, m = len(s), len(t)
    i = j = 0
    while i < n and j < m:
        if s[i] == t[j]:
            i += 1
        j += 1
    return i == n


def isSubsequence(self, s: str, t: str) -> bool:
    i = 0
    for k in t:
        if i < len(s) and k == s[i]:
            i += 1
    return i == len(s)

# def isSubsequence(self, s: str, t: str) -> bool:
#         if s == "":
#             return True
#         i = 0
#         for c in t:
#             if i < len(s) and s[i] == c:
#                 i += 1
#         return i == len(s)


def isSubsequence(self, s: str, t: str) -> bool:
    if not s:
        return True
    if s[0] in t:
        inx = t.index(s[0])
        return self.isSubsequence(s[1:], t[inx+1:])
    return False


return True if not s else self.isSubsequence(s[1:], t[t.index(s[0])+1:]) if s[0] in t else False



def isSubsequence(self, s: str, t: str) -> bool:
    if not s:
        return True
    for i in t:
        if s[0] == i:
            s = s[1:]
        if not s:
            return True
    return False



def isSubsequence(self, s: str, t: str) -> bool:
    n, m = len(s), len(t)
    f = [[0] * 26 for _ in range(m)]
    f.append([m] * 26)

    for i in range(m - 1, -1, -1):
        for j in range(26):
            f[i][j] = i if ord(t[i]) == j + ord('a') else f[i + 1][j]
    
    add = 0
    for i in range(n):
        if f[add][ord(s[i]) - ord('a')] == m:
            return False
        add = f[add][ord(s[i]) - ord('a')] + 1
    
    return True


"""
public boolean isSubsequence(String s, String t) {
    int sLen = s.length(), tLen = t.length();
    if (sLen > tLen) return false;
    if (sLen == 0) return true;
    boolean[][] dp = new boolean[sLen + 1][tLen + 1];
    for (int j = 0; j <= tLen; j++) {
        dp[0][j] = true;
    }

    for (int i = 1; i <= sLen; i++) {
        for (int j = 1; j <= tLen; j++) {
            if (s.charAt(i - 1) == t.charAt(j - 1)) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = dp[i][j - 1];
            }
        }
    }
    return dp[sLen][tLen];	
}



"""









