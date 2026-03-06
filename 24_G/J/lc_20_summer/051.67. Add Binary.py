"""
051.67. Add Binary
二进制求和


Given two binary strings, return their sum (also a binary string).

The input strings are both non-empty and contains only characters 1 or 0.

Example 1:

Input: a = "11", b = "1"
Output: "100"
Example 2:

Input: a = "1010", b = "1011"
Output: "10101"
 

Constraints:

Each string consists only of '0' or '1' characters.
1 <= a.length, b.length <= 10^4
Each string is either "0" or doesn't contain any leading zero.




"""

def addBinary(self, a, b) -> str:
    return '{0:b}'.format(int(a, 2) + int(b, 2))
    return bin(int(a, 2) + int(b, 2))[2:]
    return bin(eval('0b' + a) + eval('0b' + b))[2:]
    return f"{int(a,2)+int(b,2):b}"


def addBinary(self, a, b) -> str:
    x, y = int(a, 2), int(b, 2)
    while y:
        x, y = x ^ y, (x & y) << 1
    return bin(x)[2:]



# lc
def addBinary(self, a, b) -> str:
    n = max(len(a), len(b))
    a, b = a.zfill(n), b.zfill(n)
    
    carry = 0
    answer = []
    for i in range(n - 1, -1, -1):
        if a[i] == '1':
            carry += 1
        if b[i] == '1':
            carry += 1
            
        if carry % 2 == 1:
            answer.append('1')
        else:
            answer.append('0')
        
        carry //= 2
    
    if carry == 1:
        answer.append('1')
    answer.reverse()
    return ''.join(answer)


def addBinary(self, a: str, b: str) -> str:
        if a == '0' and b == '0':
            return '0'
        else:
            x = 0
            for i in range(1, len(a)+1):
                x += int(a[-i]) * pow(2, i-1)
            for i in range(1, len(b)+1):
                x += int(b[-i]) * pow(2, i-1)
            y = ''
            while x > 0:
                x, z = divmod(x, 2)
                y = str(z) + y
            return y


def addBinary(self, a: str, b: str) -> str:
        r, p = '', 0
        d = len(b) - len(a)
        a = '0' * d + a
        b = '0' * -d + b
        for i, j in zip(a[::-1], b[::-1]):
            s = int(i) + int(j) + p
            r = str(s % 2) + r
            p = s // 2
        return '1' + r if p else r


# recursion
def addBinary(self, a: str, b: str) -> str:
        if a == '': return b
        if b == '': return a
        if a[-1] == '1' and b[-1] == '1':
            return self.addBinary(self.addBinary(a[:-1],b[:-1]),'1')+'0'
        elif a[-1] == '0' and b[-1] == '0':
            return self.addBinary(a[:-1],b[:-1])+'0'
        else:
            return self.addBinary(a[:-1],b[:-1])+'1'



# d
def addBinary(self, a: str, b: str) -> str:
    c = int(a) + int(b)
    l = list(str(c))
    l = l[::-1] + ["0"]
    for i in range(len(l)-1):
        if l[i] == "3":
            l[i] = "1"
            l[i+1] = str(int(l[i+1]) + 1)
        if l[i] == "2":
            l[i] = "0"
            l[i+1] = str(int(l[i+1]) + 1)
    l = l[::-1]
    if l[0] == "0":
        return "".join(l[1:])
    else:
        return "".join(l)


def addBinary(self, a: str, b: str) -> str:
	if a == "":
        return b
    if b == "":
        return a
    a_2 = int(a,2)
    b_2 = int(b,2)
    carry = 1
    while carry != 0:
        carry = (a_2 & b_2)<<1
        a_2 = a_2 ^ b_2
        b_2 = carry
    return bin(a_2)[2:]        


def addBinary(self, a: str, b: str) -> str:
    ans = ''
    carry = 0
    a = list(a)
    b = list(b)
    while a or b or carry:
        if a:
            carry += int(a[-1])
            a.pop()
        if b:
            carry += int(b[-1])
            b.pop()
        
        ans = str(carry %2) + ans
        carry = carry//2
    return ans


def addBinary(self, a: str, b: str) -> str:
        res = ""
        carry = 0
        i = len(a) - 1
        j = len(b) - 1
        while i >=0 or j >= 0 or carry:
            tmp1 = int(a[i]) if i >= 0 else 0
            tmp2 = int(b[j]) if j >= 0 else 0
            carry, t = divmod(tmp1 + tmp2 + carry, 2)
            res = str(t) + res
            i -= 1
            j -= 1
        return res


def addBinary(self, a: str, b: str) -> str:
        r, p = '', 0
        d = len(b) - len(a)
        # 高位不齐补0：a = '0101' b = '1101'
        a = '0' * d + a
        b = '0' * -d + b
        for i, j in zip(a[::-1], b[::-1]):  # 逆向打包为元组(i,j=id,name)
            s = int(i) + int(j) + p
            r = str(s % 2) + r  # 求余;逆向相加 != (r += str(s % 2))
            p = s // 2  # 取整
        return '1' + r if p else r  
        # p(true),return '1' + r; p(fasle),return r



def addBinary(self, a: str, b: str) -> str:
    if len(a) < len(b): 
        a, b = b, a
    n = len(a)
    b = '0'*(n - len(b)) + b    #补齐 b 不足的位为 0
    result = ''
    summ = 0    #进位值
    for i in range(n):
        a_1 = int(a[-i-1])
        b_1 = int(b[-i-1])
        result = str((a_1 + b_1 + summ) % 2) + result    #当前位数相加模 2 ，链接更小位数的值
        summ = (a_1 + b_1 + summ) // 2    #当前位数之和整除二，得到下一位运算的进位值
    
    if summ == 1:    #判断最高位是否需要进位
        result = '1' + result
    return result


def addBinary(self, a, b):
    res, carry = '', 0
    i, j = len(a) - 1, len(b) - 1
    while i >= 0 or j >= 0 or carry:
        curval = (i >= 0 and a[i] == '1') + (j >= 0 and b[j] == '1')
        carry, rem = divmod(curval + carry, 2)
        res = `rem` + res
        i -= 1
        j -= 1
    return res


def addBinary(self, a, b):
    result = ''
    index = 0
    
    carry = '0'
    while index < max(len(a), len(b)) or carry == '1':
        num_a = a[-1 - index] if index < len(a) else '0'
        num_b = b[-1 - index] if index < len(b) else '0'
        
        val = self.to_int(num_a) + self.to_int(num_b) + self.to_int(carry)
        result = "%s%s" % (val % 2, result)
        
        carry = '1' if val > 1 else '0'
        index += 1

    return result

def to_int(self, c):
    if c == '1':
        return 1
    elif c == '0':
        return 0


def addBinary(self, a, b):
    result = ''
    index = 0
    
    carry = '0'
    while index < max(len(a), len(b)) or carry == '1':
        num_a = a[-1 - index] if index < len(a) else '0'
        num_b = b[-1 - index] if index < len(b) else '0'
        
        val = int(num_a) + int(num_b) + int(carry)
        result = str(val % 2) + result
        
        carry = '1' if val > 1 else '0'
        index += 1

    return result


def addBinary(self, a: str, b: str) -> str:
    carry = 0
    result = ""
    i, j = len(a) - 1, len(b) - 1
    while i >= 0 or j >= 0:
        a_digit = int(a[i]) if i >= 0 else 0
        b_digit = int(b[j]) if j >= 0 else 0
        _sum = a_digit + b_digit + carry
        digit = _sum % 2
        carry = _sum // 2
        result = str(digit) + result
        i -= 1
        j -= 1
    if carry:
        result = str(carry) + result
    return result

































