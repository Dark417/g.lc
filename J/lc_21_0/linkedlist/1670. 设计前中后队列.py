# 1670. 设计前中后队列
class LinkedListNode:
    def __init__(self, val: int):
        self.val = val
        self.prev = None
        self.succ = None

class LinkedList:
    def __init__(self):
        self.head = LinkedListNode(42)
        self.tail = LinkedListNode(42)
        self.head.succ = self.tail
        self.tail.prev = self.head
        self.size = 2
    
    def __str__(self):
        ret = list()
        cur = self.head
        while cur:
            ret.append(cur.val)
            cur = cur.succ
        return str(ret)

    def insert(self, it: LinkedListNode, val: int):
        self.size += 1
        node = LinkedListNode(val)
        it.prev.succ = node
        node.prev = it.prev
        it.prev = node
        node.succ = it
    
    def erase(self, it: LinkedListNode) -> LinkedListNode:
        self.size -= 1
        ret = it.succ
        it.prev.succ = it.succ
        it.succ.prev = it.prev
        return ret
    
    def advance(self, it: LinkedListNode, dt: int) -> LinkedListNode:
        if dt > 0:
            for _ in range(dt):
                it = it.succ
        elif dt < 0:
            for _ in range(-dt):
                it = it.prev
        return it
    
class FrontMiddleBackQueue:

    def __init__(self):
        self.q = LinkedList()
        self.it = self.q.head
        self.ptrpos = 0

    def pushFront(self, val: int) -> None:
        # 指针不指向哑头节点
        if self.ptrpos != 0:
            self.ptrpos += 1
        self.q.insert(self.q.head.succ, val)

    def pushMiddle(self, val: int) -> None:
        pos = self.q.size // 2
        # 均摊 O(1)
        self.it = self.q.advance(self.it, pos - self.ptrpos)
        self.q.insert(self.it, val)
        self.ptrpos = pos + 1
        
    def pushBack(self, val: int) -> None:
        # 指针指向哑尾节点
        if self.ptrpos == self.q.size - 1:
            self.ptrpos += 1
        self.q.insert(self.q.tail, val)

    def popFront(self) -> int:
        if self.q.size == 2:
            return -1
        ret = self.q.head.succ.val
        if self.ptrpos == 1:
            self.it = self.q.erase(self.it)
        else:
            self.q.erase(self.q.head.succ)
            # 指针不指向哑头节点
            if self.ptrpos != 0:
                self.ptrpos -= 1
        return ret

    def popMiddle(self) -> int:
        if self.q.size == 2:
            return -1
        pos = (self.q.size - 1) // 2
        # 均摊 O(1)
        self.it = self.q.advance(self.it, pos - self.ptrpos)
        ret = self.it.val
        self.it = self.q.erase(self.it)
        self.ptrpos = pos
        return ret

    def popBack(self) -> int:
        if self.q.size == 2:
            return -1
        ret = self.q.tail.prev.val
        if self.ptrpos == self.q.size - 2:
            self.it = self.q.erase(self.it)
        else:
            self.q.erase(self.q.tail.prev)
            # 指针指向哑尾节点
            if self.ptrpos == self.q.size:
                self.ptrpos -= 1
        return ret







def __init__(self):
    self.A, self.B = collections.deque(), collections.deque()

def pushFront(self, val):
    self.A.appendleft(val)
    self.balance()

def pushMiddle(self, val):
    if len(self.A) > len(self.B):
        self.B.appendleft(self.A.pop())
    self.A.append(val)

def pushBack(self, val):
    self.B.append(val)
    self.balance()

def popFront(self):
    val = self.A.popleft() if self.A else -1
    self.balance()
    return val

def popMiddle(self):
    val = (self.A or [-1]).pop()
    self.balance()
    return val

def popBack(self):
    val = (self.B or self.A or [-1]).pop()
    self.balance()
    return val

# keep A.size() >= B.size()
def balance(self):
    if len(self.A) > len(self.B) + 1:
        self.B.appendleft(self.A.pop())
    if len(self.A) < len(self.B):
        self.A.append(self.B.popleft())


            
def __init__(self):
        self.q = list()

def pushFront(self, val: int) -> None:
    self.q[0:0] = [val]

def pushMiddle(self, val: int) -> None:
    # 注意正确计算位置
    pos = len(self.q) // 2
    self.q[pos:pos] = [val]

def pushBack(self, val: int) -> None:
    self.q.append(val)

def popFront(self) -> int:
    if not self.q:
        return -1
    ret = self.q[0]
    self.q[0:1] = []
    return ret

def popMiddle(self) -> int:
    if not self.q:
        return -1
    # 注意正确计算位置
    pos = (len(self.q) - 1) // 2
    ret = self.q[pos]
    self.q[pos:pos+1] = []
    return ret

def popBack(self) -> int:
    if not self.q:
        return -1
    return self.q.pop()







