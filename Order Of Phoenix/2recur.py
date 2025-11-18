# 2025.11.18
# 2025.8.7
# su su
# 2Recursion





#hard################################################################
224. 基本计算器





#mid################################################################
2. 两数相加


#ez################################################################
509. 斐波那契数

	70. 爬楼梯




231. 2 的幂
	326. 3 的幂
	342. 4的幂




3304. 找出第 K 个字符 I



LCR 187. 破冰游戏












#hard################################################################
224. 基本计算器
def calculate(self, s: str) -> int:
    ops = [1]
    sign = 1
    ret = 0
    n = len(s)
    i = 0
    while i < n:
        if s[i] == ' ':
            i += 1
        elif s[i] == '+':
            sign = ops[-1]
            i += 1
        elif s[i] == '-':
            sign = -ops[-1]
            i += 1
        elif s[i] == '(':
            ops.append(sign)
            i += 1
        elif s[i] == ')':
            ops.pop()
            i += 1
        else:
            num = 0
            while i < n and s[i].isdigit():
                num = num * 10 + ord(s[i]) - ord('0')
                i += 1
            ret += num * sign
    return ret




#ez################################################################

509. 斐波那契数
def fib(self, n: int) -> int:
    if n <= 1:
        return n
    return self.fib(n-1) + self.fib(n-2)

    70. 爬楼梯
    def climbStairs(self, n: int) -> int:
        @cache
        def dfs(i):
            if i <= 1:
                return 1
            return dfs(i - 1) + dfs(i - 2)
        return dfs(n)





231. 2 的幂
def isPowerOfTwo(self, n: int) -> bool:
	return n > 0 and n & (n - 1) == 0


def isPowerOfTwo(self, n: int) -> bool:
    if n <= 0 or n == 1:
        return n == 1
    return n % 2 == 0 and self.isPowerOfTwo(n // 2)

def isPowerOfTwo(self, n: int) -> bool:
    while n > 1:
        n /= 2
    return n == 1

def isPowerOfTwo(self, n: int) -> bool:
    i = 1
    while i <= n:
        if i == n:
            return True
        i *= 2
    return False


    326. 3 的幂
    def isPowerOfThree(self, n: int) -> bool:
        if n == 3 or n == 1:
            return True
        elif n < 3:
            return False
        return self.isPowerOfThree(n / 3)

    def isPowerOfThree(self, n: int) -> bool:
        while n and n % 3 == 0:
            n /= 3
        return n == 1

    342. 4的幂
	def isPowerOfFour(self, n: int) -> bool:
	    if n == 0:
	        return False
	    elif n == 1:
	        return True
	    
	    elif n % 4 != 0:
	        return False
	    return self.isPowerOfFour(n//4)



LCR 123. 图书整理 I
def reverseBookList(self, head: Optional[ListNode]) -> List[int]:
    return self.reverseBookList(head.next) + [head.val] if head else []

def reverseBookList(self, head: ListNode) -> List[int]:
    stack = []
    while head:
        stack.append(head.val)
        head = head.next
    return stack[::-1]





LCR 187. 破冰游戏









#mid################################################################
2. 两数相加















