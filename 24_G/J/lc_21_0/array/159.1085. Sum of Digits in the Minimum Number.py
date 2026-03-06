"""
159.1085. Sum of Digits in the Minimum Number
最小元素各数位之和

160.258. Add Digits
各位相加



给你一个正整数的数组 A。

然后计算 S，使其等于数组 A 当中最小的那个元素各个数位上数字之和。

最后，假如 S 所得计算结果是 奇数 的请你返回 0，否则请返回 1。

 

示例 1:

输入：[34,23,1,24,75,33,54,8]
输出：0
解释：
最小元素为 1，该元素各个数位上的数字之和 S = 1，是奇数所以答案为 0。
示例 2：

输入：[99,77,33,66,55]
输出：1
解释：
最小元素为 33，该元素各个数位上的数字之和 S = 3 + 3 = 6，是偶数所以答案为 1。
 

提示：

1 <= A.length <= 100
1 <= A[i].length <= 100

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/sum-of-digits-in-the-minimum-number
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

def sumOfDigits(self, A: List[int]) -> int:
    return 1- sum(int(i) for i in str(min(A))) % 2


return sum(map(int, str(min(A)))) & 1 ^ 1



def sumOfDigits(self, A: List[int]) -> int:
    x = min(A)
    r = 0
    while x >= 10:
        r+= x-10*(x//10)
        x = x//10
    r += x
    return 1-r%2



"""
160.258. Add Digits
各位相加
"""

def addDigits(self, num: int) -> int:
	return num % 9 or 9 if num else 0

def addDigits(self, num):
    while(num >= 10):
        temp = 0
        while(num > 0):
            temp += num % 10
            num //= 10
        num = temp
    return num



# caikehe
def addDigits1(self, num):
    return num - ((num-1)/9)*9 if num > 0 else 0
    
def addDigits2(self, num):
    return (num-1)%9 + 1 if num > 0 else 0
    
def addDigits3(self, num):
    return num and (num-1)%9 + 1
  
# Recursively  
def addDigits4(self, num):
    if 0<= num <= 9:
        return num
    tmp = 0
    while num:
        tmp += num % 10
        num //= 10
    return self.addDigits(tmp)
    
# Iteratively
def addDigits(self, num):
    if num == 0:
        return 0
    while num:
        if 1 <= num <= 9:
            return num
        tmp = 0
        while num:
            tmp += num % 10
            num //= 10
        num = tmp



























































































