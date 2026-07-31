"""
216.338. Counting Bits
比特位计数


Given a non negative integer number num. For every numbers i in the range 0 ≤ i ≤ num 
calculate the number of 1's in their binary representation and return them as an array.

Example 1:

Input: 2
Output: [0,1,1]
Example 2:

Input: 5
Output: [0,1,1,2,1,2]
Follow up:

It is very easy to come up with a solution with run time O(n*sizeof(integer)). But can 
you do it in linear time O(n) /possibly in a single pass?
Space complexity should be O(n).
Can you do it like a boss? Do it without using any builtin function like __builtin_popcount 
in c++ or in any other language.



https://leetcode-cn.com/problems/counting-bits/solution/fen-zhi-fa-de-counting-1-bits-by-ai-ji-mo-de-shi-g/
"""



"{0:b}".format(37)



return [bin(i).count('1') for i in range(num+1)]
return list(map(lambda x:bin(x).count('1'), range(num+1)))



def countBits(self, num: int) -> List[int]:
    out = [0]
    for i in range(1, num + 1):
        out.append(out[i >> 1] + 1 if i & 1 else out[i >> 1])                   
    return out



def countBits(self, num: int) -> List[int]:
    binary_representation = {0: 0, 1: 1, 2: 1}
    if num == 1:
        return [0, 1]
    if num == 0:
        return [0]
    for x in range(3, num+1):
        quotient, reminder = divmod(x, 2)
        binary_representation[x] = binary_representation[quotient] + binary_representation[reminder]
    return list(binary_representation.values())



def countBits(self, num):
    iniArr = [0]
    if num > 0:
        amountToAdd = 1
        while len(iniArr) < num + 1:
            iniArr.extend([x+1 for x in iniArr])
    
    return iniArr[0:num+1]


def countBits(self, num):
    res = [0]
    while len(res) <= num:
        res += [i+1 for i in res]
    return res[:num+1]



def countBits(self, num):
    answer = [0, 1]
    while len(answer) <= num:
        answer.extend(map(lambda x:x+1, answer))
    return answer[:num+1]



def countBits(self, num: int) -> List[int]:
    r = [0]
    while len(r) * 2 - 1 <= num:
        r += [1 + e for e in r]
    r += [1 + e for e in r[:num - len(r) + 1]]
    return r



def countBits(self, num):
    setBits = [0] * (num+1)
    # (i & (i -1)) is actually Brian Kernighan’s Algorithm, so always keep it handy for counting ones
    for i in range(1 ,num+1):
        setBits[i] = setBits[i & (i-1)] + 1
    return setBits



def countBits(self, num):
    res=[0]
    for i in xrange(1,num+1):
        res.append(res[i>>1]+(i&1))
    return res



def countBits(self, num: int) -> List[int]:
    counter = [0]
    for i in range(1, num+1):
        counter.append(counter[i >> 1] + i % 2)
    return counter











def countBits(self, num: int) -> List[int]:
    res = [0]
    for i in range(1,num+1):
        if i%2 == 0:
            res.append(res[i//2])
        else:
            res.append(res[i-1] + 1)
    return res


def countBits(self, num: int) -> List[int]:
    #简单思路：转为bin统计1的个数
    num = list(range(num+1))
    size = len(num)
    for i in range(size):
        num[i] = bin(num[i])[2:]
        num[i] = num[i].count("1")
    return num



# https://leetcode-cn.com/problems/counting-bits/solution/yu-89ge-lei-bian-ma-si-lu-ji-ben-yi-zhi-by-justyou/
#
def countBits(self, num: int) -> List[int]:
    idx,res = 0, []
    res.append(0)

    while idx <= num:
        length = len(res)
        for i in range(length):
            res.append(res[i]+1)
            idx += 1

    return res[:num+1]



def countBits(num):
    """
        1. dp问题: dp[i] = dp[i>>1] + (i&1).
            i>>1代表前一个二进制位的次数,
            i&1代表i的末尾是否为1
    """
    dp = [0]
    for i in range(1, num + 1):
        dp.append(dp[i>>1] + (i&1))
    
    return dp







































































