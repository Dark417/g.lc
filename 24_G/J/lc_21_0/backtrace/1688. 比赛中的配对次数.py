# 1688. 比赛中的配对次数


return n - 1


def numberOfMatches(self, n: int) -> int:
    res = 0
    while n > 1:
        if n % 2:
            res += (n-1) // 2
            n = (n-1) // 2 + 1
        else:
            n //= 2
            res += n
    return res


def numberOfMatches(self, n: int) -> int:
    if n == 1:
        return 0
    return self.numberOfMatches(n - n//2) + n//2

    return n-1


def numberOfMatches(self, n: int) -> int:
	if n < 2:
		return 0
	if n == 2:
		return 1
	if n % 2:
		return (n-1)//2 + self.numberOfMatches(n//2 + 1)
	else:
		return n//2 + self.numberOfMatches(n//2)


