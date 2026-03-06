# 738. 单调递增的数字

def monotoneIncreasingDigits(self, N):
    i = 1
    sN = list(str(N))
    while i < len(sN) and sN[i] >= sN[i - 1]:
        i += 1
    if i < len(sN):
        while i > 0 and sN[i - 1] > sN[i]:
            sN[i - 1] = str(int(sN[i - 1]) - 1)
            i -= 1
        for j in range(i + 1, len(sN)):
            sN[j] = "9"
    return "".join(sN).lstrip("0")


def monotoneIncreasingDigits(self, N: int) -> int:
    ones = 111111111
    result = 0
    for _ in range(9):
        while result + ones > N:
            ones //= 10
        result += ones
    return result



































