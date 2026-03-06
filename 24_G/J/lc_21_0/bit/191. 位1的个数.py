# 191. 位1的个数


def hammingWeight(self, n: int) -> int:
    mask = 1
    bit = 0
    for i in range(32):
    	if n & mask:
        if n & mask != 0:
            bit += 1
        mask <<= 1
    return bit























