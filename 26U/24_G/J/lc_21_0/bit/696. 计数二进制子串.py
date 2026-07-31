# 696. 计数二进制子串

def countBinarySubstrings(self, s: str) -> int:
    l = []
    i = 0
    res = 0

    while i < len(s):
        val = s[i]
        cnt = 0
        while i < len(s) and s[i] == val:
            cnt += 1
            i += 1
        l.append(cnt)

    if len(l) <= 0:
        return 0
    else:
        for i in range(1, len(l)):
            res += min(l[i], l[i-1])

    return res


def countBinarySubstrings(self, s: str) -> int:
    i = 0
    res = 0
    last = 0

    while i < len(s):
        cnt = 0
        val = s[i]

        while i < len(s) and s[i] == val:
            cnt += 1
            i += 1

        res += min(last, cnt)
        last = cnt

    return res


def countBinarySubstrings(self, s: str) -> int:
	i = 0
	res = 0
	last = 0

	while i < len(s):
		cnt = 0
		val = s[i]

		while i < len(s) and s[i] = val:
			cnt += 1
			i += 1

		res += min(last, min)
		last = cnt

	return res







def countBinarySubstrings(self, s: str) -> int:
    l = []
    i = 0
    res = 0
    cnt = 1

    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            cnt += 1
        else:
            l.append(cnt)
            cnt = 1
    if len(s) >= 2 and s[-1] == s[-2]:
        l.append(cnt)
    else:
        l.append(1)

    if len(l) <= 0:
        return 0
    else:
        for i in range(1, len(l)):
            res += min(l[i], l[i-1])

    return res



def countBinarySubstrings(self, s: str) -> int:
    seq = [0, 1]
    res = []
    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            seq[1] += 1
        else:
            res.append(min(seq))
            seq[0] = seq[1]
            seq[1] = 1
    res.append(min(seq))
    return sum(res)










