"""
217.191. Number of 1 Bits
位1的个数

Write a function that takes an unsigned integer and return the number of '1' bits it 
has (also known as the Hamming weight).

 

Example 1:

Input: 00000000000000000000000000001011
Output: 3
Explanation: The input binary string 00000000000000000000000000001011 has a total of three '1' bits.
Example 2:

Input: 00000000000000000000000010000000
Output: 1
Explanation: The input binary string 00000000000000000000000010000000 has a total of one '1' bit.
Example 3:

Input: 11111111111111111111111111111101
Output: 31
Explanation: The input binary string 11111111111111111111111111111101 has a total of thirty one '1' bits.
"""


return bin(n).count('1')
return str(bin(n)).count('1')

return f'{n:b}'.count('1')

return sum(1 for i in bin(n)[2:] if i>'0')



return self.hammingWeight(n & n-1, count+1) if n!=0 else count


return len([i for i in range(32) if (1<<i)&n])  

return sum((n>>i&1 for i in range(32)))
return (bin(n)[2:]).count("1")



def bitCountA(n):
    count = 0
    while (n != 0):
        if (n & 1 != 0):
            count += 1
        n = n>>1
    return count


def hammingWeight(self, n):
    count = 0
    while (n != 0):
        n = n & (n - 1)
        count += 1
    return count


def hammingWeight(self, n: int) -> int:
        count = 0
        while n > 0:
            n &= (n - 1)
            count += 1
        return count



def hammingWeight1(self, n):
    res = 0
    for i in xrange(32):
        # res += (n & 1 << i != 0)
        res += (n >> i & 1)
    return res


def hammingWeight(self, n):
    res = 0 
    # Ex. bin(2) = '0b10'. We don't need first two digit 
    for i in range(len(bin(n))-2):
        # test if ith digit has '1'
        if n & (1<<i): 
            res += 1 
    return res



def hammingWeight(self, n: int) -> int:
        num_of_1s = 0
        for i in range(64):
            num_of_1s += (n & 1)
            n = n >> 1
        return num_of_1s


def hammingWeight(self, n):
    res = 0
    while n:
        res += n&1
        n /= 2
    return res


def hammingWeight(self, n):
    count = 0
    while n:
        count = count + n % 2
        n = n // 2
    return count


def hammingWeight(n):
    r = 0
    while n:
        if n & 1:
            r += 1
        n >>= 1
    return r


def using_inbuilt_counter(self, n):
    counter = collections.Counter(bin(n)[2:])
    return counter.get("1", 0)

def using_bit_manipulation(self, n):
    count = 0
    while n:
        if n & 1: count += 1
        n = n >> 1
    return count



def hammingWeight(self, n):
    cnt = 0
    while n > 0:
        cnt += 1
        n &= n-1
    return cnt



def hammingWeight(self, n):
    count = 0
    i = 31
    while i >= 0:
        if n > 2 ** i:
            n = n - 2 ** i
            count = count + 1
        elif n == 2 ** i:
            count = count + 1
            break
        i = i - 1
    return count



count = 0
while n:
	if n%2: count += 1
	n//=2
return count



count = 0
while n:
	n &= (n-1)
	count += 1
return count



if not n: return 0
return (n%2)+self.hammingWeight(n//2)



if not n: return 0
return 1+self.hammingWeight(n&(n-1))




# https://leetcode.com/problems/number-of-1-bits/discuss/377550/Python-multiple-solutions-including-O(1)
def hammingWeight(self, n):
    mask_sum_2bit = 0x55555555
    mask_sum_4bit = 0x33333333
    mask_sum_8bit = 0x0F0F0F0F
    mask_sum_16bit = 0x00FF00FF
    mask_sum_32bit = 0x0000FFFF
    
    n = (n & mask_sum_2bit) + ((n >> 1) & mask_sum_2bit)
    n = (n & mask_sum_4bit) + ((n >> 2) & mask_sum_4bit)
    n = (n & mask_sum_8bit) + ((n >> 4) & mask_sum_8bit)
    n = (n & mask_sum_16bit) + ((n >> 8) & mask_sum_16bit)
    n = (n & mask_sum_32bit) + ((n >> 16) & mask_sum_32bit)
    
    return n

























































