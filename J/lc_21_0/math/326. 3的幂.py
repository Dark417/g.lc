# 326. 3的幂

return n > 0 and 1162261467 % n == 0
return n > 0 == 3**19 % n



def isPowerOfThree(self, n: int) -> bool:
    while n > 1:
        n /= 3
    return n == 1

def isPowerOfThree(self, n: int) -> bool:
	if n < 1:
		return False
	while n % 3 == 0: # not n % 3
		n /= 3
	return n == 1


def isPowerOfThree(self, n: int) -> bool:
    if n == 0:
        return False
    if n == 1:
        return True
    if n % 3:
        return False
    return self.isPowerOfThree(n/3)



