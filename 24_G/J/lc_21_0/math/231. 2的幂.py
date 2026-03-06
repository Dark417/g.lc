# 231. 2的幂

return n > 0 and n & (n - 1) == 0



def isPowerOfTwo(self, n):
    if n == 0:
        return False
    return n & (-n) == n


return bin(n).count('1') == 1 if n > 0 else False



def isPowerOfTwo(self, n):
    if n == 0:
        return False
    return n & (n - 1) == 0





