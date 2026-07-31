# 67. 二进制求和

def addBinary(self, a, b) -> str:
    return '{0:b}'.format(int(a, 2) + int(b, 2))




def addBinary(self, a, b) -> str:
    x, y = int(a, 2), int(b, 2)
    while y:
        answer = x ^ y
        carry = (x & y) << 1
        x, y = answer, carry
    return bin(x)[2:]





def addBinary(self, a: str, b: str) -> str:
    l1 = len(a) - 1
    l2 = len(b) - 1
    car = 0
    ans = ""

    while l1 >= 0 or l2 >=0:
        x = int(a[l1]) if l1 >= 0 else 0
        y = int(b[l2]) if l2 >= 0 else 0

        r  = car + x + y
        car = r // 2
        r = r % 2

        ans = str(r) + ans 
        l1 -= 1
        l2 -= 1
    if car:
        ans = str(car) + ans
    return ans