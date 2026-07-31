# 367. 有效的完全平方数




def isPerfectSquare(self, num: int) -> bool:
    l, r = 1, num//2 + 1
        
    while l <= r:
        mid = (l + r) >> 1
        
        if mid * mid == num:
            return True
        if mid * mid > num:
            r = mid - 1
        else:
            l = mid + 1
    return False



def isPerfectSquare(self, num: int) -> bool:
    if num < 2:
        return True
    
    x = num // 2
    while x * x > num:
        x = (x + num // x) // 2
    return x * x == num


































