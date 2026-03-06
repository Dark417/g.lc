# 346. 数据流中的移动平均值

def __init__(self, size: int):
    self.size = size
    self.queue = deque()
    self.sum = 0

def next(self, val: int) -> float:
    self.sum += val
    self.queue.append(val)
    if len(self.queue) > self.size:
        self.sum -= self.queue.popleft()
    return self.sum / len(self.queue)




def __init__(self, size: int):
    self.size = size
    self.queue = deque()
    self.window_sum = 0
    self.count = 0

def next(self, val: int) -> float:
    self.count += 1
    self.queue.append(val)
    tail = self.queue.popleft() if self.count > self.size else 0
    self.window_sum = self.window_sum - tail + val
    return self.window_sum / min(self.size, self.count)



def __init__(self, size: int):
    self.size = size
    self.queue = [0] * self.size
    self.head = self.window_sum = 0
    self.count = 0

def next(self, val: int) -> float:
    self.count += 1
    tail = (self.head + 1) % self.size
    self.window_sum = self.window_sum - self.queue[tail] + val
    self.head = (self.head + 1) % self.size
    self.queue[self.head] = val
    return self.window_sum / min(self.size, self.count)





def __init__(self, size: int):
    self.size = size
    self.nums = []

def next(self, val: int) -> float:
    self.nums.append(val)
    if len(self.nums) < self.size:
        return sum(self.nums) / len(self.nums)
    else:
        return sum(self.nums[-self.size:]) / self.size



def __init__(self, size: int):
    self.size = size
    self.queue = []
    
def next(self, val: int) -> float:
    size, queue = self.size, self.queue
    queue.append(val)
    window_sum = sum(queue[-size:])
    return window_sum / min(len(queue), size)








