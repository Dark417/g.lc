"""
245.202. Happy Number
快乐数


Write an algorithm to determine if a number n is "happy".

A happy number is a number defined by the following process: Starting with any 
positive integer, replace the number by the sum of the squares of its digits, and 
repeat the process until the number equals 1 (where it will stay), or it loops endlessly 
in a cycle which does not include 1. Those numbers for which this process ends in 1 are 
happy numbers.

Return True if n is a happy number, and False if not.

Example: 

Input: 19
Output: true
Explanation: 
12 + 92 = 82
82 + 22 = 68
62 + 82 = 100
12 + 02 + 02 = 1

"""

def isHappy(self, n: int) -> bool:
    dic = {}
    while 1:
        r = t = 0
        while 1:
            if n >= 10:
                r = n%10
                n = n//10
                t += r*r
            else:
                t += n*n
                break
        if t == 1:
            return True
        if str(t) in dic:
            return False
        else:
            dic[str(t)] = 1
        n = t

# set



def isHappy(self, n: int) -> bool:
    def get_next(n):
        total_sum = 0
        while n > 0:
            n, digit = divmod(n, 10)
            total_sum += digit ** 2
        return total_sum

    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = get_next(n)

    return n == 1




def isHappy(self, n: int) -> bool:
    # 初始化 visited
    visited = set()
    # 当 n != 1，并且没见过 n 时进行判断
    while n != 1 and n not in visited:
        # 把 n 放入 visited
        visited.add(n)
        # 计算下一轮的数字
        nxt = 0
        # 计算 n 的各位数字平方和
        while n != 0:
            nxt += (n % 10) ** 2
            n //= 10
        # 把下一轮的数字设定为 n
        n = nxt
    # 判断 n 的最终结果是否为 1
    return n == 1




def isHappy(self, n):
    mem = set()
    while n != 1:
        n = sum([int(i) ** 2 for i in str(n)])
        if n in mem:
            return False
        else:
            mem.add(n)
    else:
        return True


def isHappy(self, n: int) -> bool:
    def next_num(num):
        return sum(map(lambda x:int(x)**2, str(num)))
    slow, fast = n, next_num(n)
    while slow != fast and fast != 1:
        slow = next_num(slow)
        fast = next_num(next_num(fast))
    return fast == 1 or not slow == fast


def getNext(self, n: int) -> int:
    next_n = 0
    while(n != 0):
        next_n += (n % 10) ** 2
        n = n // 10
    return next_n

def isHappy(self, n: int) -> bool:
    slow = n
    fast = self.getNext(n)
    while(fast != 1 and slow != fast):
        slow = self.getNext(slow)
        fast = self.getNext(self.getNext(fast))
    return fast == 1




















































