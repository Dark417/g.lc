# 面试题 01.06. 字符串压缩


def compressString(self, S: str) -> str:
    i = 0
    res = ""

    while i < len(S):
        cnt = 0
        val = S[i]

        while i < len(S) and S[i] == val:
            cnt += 1
            i += 1
        res += S[i-1] + str(cnt)
    return res if len(res) < len(S) else S



def compressString(self, S: str) -> str:
    if not S:
        return ""
    ch = S[0]
    ans = ''
    cnt = 0
    for c in S:
        if c == ch:
            cnt += 1
        else:
            ans += ch + str(cnt)
            ch = c
            cnt = 1
    ans += ch + str(cnt)
    return ans if len(ans) < len(S) else S





