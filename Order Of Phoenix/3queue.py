# 2025.8.3
# 害queue呢？
# 3queue


#core####################################################################
232. 用栈实现队列
	LCR 125. 图书整理 II
	面试题 03.04. 化栈为队

225. 用队列实现栈

622. 设计循环队列



#ez####################################################################

387. 字符串中的第一个唯一字符


1700. 无法吃午餐的学生数量


933. 最近的请求次数


346. 数据流中的移动平均值


2073. 买票需要的时间


#mid####################################################################

918. 环形子数组的最大和







#core####################################################################
232. 用栈实现队列
class MyQueue:

    def __init__(self):
        self.A = []
        self.B = []

    def push(self, x: int) -> None:
        self.A.append(x)


    def pop(self) -> int:
        peek = self.peek()
        self.B.pop()
        return peek

    def peek(self) -> int:
        if self.B:
            return self.B[-1]
        if not self.A:
            return -1
        while self.A:
            self.B.append(self.A.pop())
        return self.B[-1]

    def empty(self) -> bool:
        return not self.A and not self.B


class MyQueue:
    def __init__(self):
        self.s1 = []  # Temporary stack for pushing
        self.s2 = []  # Stack maintaining queue order

    def push(self, x: int) -> None:
        # Move s2 to s1
        while self.s2:
            self.s1.append(self.s2.pop())
        # Push new element to s1
        self.s1.append(x)
        # Move s1 back to s2 to maintain queue order
        while self.s1:
            self.s2.append(self.s1.pop())

    def pop(self) -> int:
        return self.s2.pop()  # O(1)

    def peek(self) -> int:
        return self.s2[-1]  # O(1)

    def empty(self) -> bool:
        return not self.s2  # O(1)

###
225. 用队列实现栈
class MyStack:
    def __init__(self):
        self.q1 = deque()
        self.q2 = deque()

    def push(self, x: int) -> None:
        self.q2.append(x)
        while self.q1:
            self.q2.append(self.q1.popleft())
        self.q1, self.q2 = self.q2, self.q1

    def pop(self) -> int:
        return self.q1.popleft()

    def top(self) -> int:
        return self.q1[0]

    def empty(self) -> bool:
        return not self.q1



622. 设计循环队列














#ez####################################################################

387. 字符串中的第一个唯一字符
def firstUniqChar(s: str) -> int:
    freq = Counter(s)
    
    queue = deque()
    for i, char in enumerate(s):
        if freq[char] == 1:
            queue.append((char, i))
    
    return queue[0][1] if queue else -1


def firstUniqChar(s: str) -> int:
    freq = Counter(s)
    queue = deque()
    seen = set()
    
    for i, char in enumerate(s):
        queue.append((char, i))
    
    while queue:
        char, idx = queue.popleft()
        if char not in seen and freq[char] == 1:
            return idx
        seen.add(char)
    
    return -1




1700. 无法吃午餐的学生数量
	def countStudents(self, students: List[int], sandwiches: List[int]) -> int:
        s1 = sum(students)
        s0 = len(students) - s1
        for n in sandwiches:
            if n == 1 and s1:
                s1 -= 1
            elif n == 0 and s0:
                s0 -= 1
            else:
                break
        return s0 + s1

	def countStudents(self, students: List[int], sandwiches: List[int]) -> int:
        cnt = Counter(students)
        for i, n in enumerate(sandwiches):
            if cnt[n] == 0:
                return len(students) - i
            cnt[n] -= 1
        return 0


933. 最近的请求次数
class RecentCounter:
	def __init__(self):
	    self.q = deque()

	def ping(self, t: int) -> int:
	    self.q.append(t)
	    while self.q[0] < t - 3000:
	        self.q.popleft()
	    return len(self.q)



346. 数据流中的移动平均值
class MovingAverage:
    def __init__(self, size: int):
        self.size = size
        self.sum = 0
        self.q = deque()
        

    def next(self, val: int) -> float:
        if len(self.q) == self.size:
            self.sum -= self.q.popleft()
        self.sum += val
        self.q.append(val)
        return self.sum / len(self.q)



2073. 买票需要的时间
def timeRequiredToBuy(self, tickets: List[int], k: int) -> int:
    ans = 0
    for i, x in enumerate(tickets):
        ans += min(x, tickets[k] if i <= k else tickets[k] - 1)
    return ans

    tk = tickets[k]
    return sum(min(t, tk - (i > k)) for i, t in enumerate(tickets))

def timeRequiredToBuy(self, tickets: List[int], k: int) -> int:
    queue = deque((i, tickets[i]) for i in range(len(tickets)))
    time = 0
    while queue:
        idx, ticket_count = queue.popleft()
        time += 1
        ticket_count -= 1
        if idx == k and ticket_count == 0:
            return time
        if ticket_count > 0:
            queue.append((idx, ticket_count))
    return time




#mid####################################################################

918. 环形子数组的最大和





1823. 找出游戏的获胜者
def findTheWinner(self, n: int, k: int) -> int:
    q = deque(range(1, n + 1))
    while len(q) > 1:
        for _ in range(k - 1):
            q.append(q.popleft())
        q.popleft()
    return q[0]

	return 1 if n == 1 else (k + self.findTheWinner(n - 1, k) - 1) % n + 1








































































