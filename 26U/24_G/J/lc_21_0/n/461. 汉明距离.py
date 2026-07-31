# 461. 汉明距离

def hammingDistance(self, x: int, y: int) -> int:
    s1 = str(bin(x))[2:]
    s2 = str(bin(y))[2:]
    s1 = "0" * (len(s2)-len(s1)) + s1 if len(s1) < len(s2) else s1
    s2 = "0" * (len(s1)-len(s2)) + s2 if len(s2) < len(s1) else s2
    
    s = 0
    
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            s += 1
    
    return s



def hammingDistance(self, x, y):
    return bin(x ^ y).count('1')



