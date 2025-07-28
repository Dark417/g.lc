# 168. Excel表列名称
def convertToTitle(self, n: int) -> str:
    def recur(n):
        n -= 1
        q, r = divmod(n, 26)
        if q <=26:
            return s[r] if q == 0 else s[q-1] + s[r]
        else:
            return recur(q) + s[r]
    
    s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return recur(n)


def convertToTitle(self, n: int) -> str:
    s = ''
    while n:
        n -= 1
        s = chr(65 + n % 26) + s
        n //= 26
    return s



return "" if num == 0 else self.
convertToTitle((num - 1) / 26) + chr((num - 1) % 26 + ord('A'))


return self.convertToTitle((num - 1) / 26) + chr((num - 1) % 26 + ord('A')) if num else ""



# 171. Excel表列序号
def titleToNumber(self, s: str) -> int:
    res = 0
    for c in s:
        res *= 26
        res += ord(c) - 64
    return res


def titleToNumber(self, s):
    ans = 0
    for x in s:
        ans *= 26
        ans += ord(x)-ord('A')+1
    return ans


def titleToNumber(self, s: str) -> int:
    res = digit = 0
    n = len(s) - 1
    while n >= 0:
        d = s[n]
        res += (ord(d) - 64) * 26**digit 
        n -= 1
        digit += 1
    return res




