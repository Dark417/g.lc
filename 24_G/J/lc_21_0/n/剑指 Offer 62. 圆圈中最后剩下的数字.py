# 剑指 Offer 62. 圆圈中最后剩下的数字



def lastRemaining(self, n: int, m: int) -> int:
    f = 0
    for i in range(2, n + 1):
        f = (m + f) % i
    return f


def lastRemaining(self, n: int, m: int) -> int:
    l = list(range(n))
    i = 0
    while len(l) > 1:
        i += m-1
        i %= len(l)
        l.pop(i)
    return l[0]


















