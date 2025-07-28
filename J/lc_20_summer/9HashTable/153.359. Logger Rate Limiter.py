"""
153.359. Logger Rate Limiter
日志速率限制器


请你设计一个日志系统，可以流式接收日志以及它的时间戳。

该日志会被打印出来，需要满足一个条件：当且仅当日志内容 在过去的 10 秒钟内没有被打印过。

给你一条日志的内容和它的时间戳（粒度为秒级），如果这条日志在给定的时间戳应该被打印出来，则返回 true，否则请返回 false。

要注意的是，可能会有多条日志在同一时间被系统接收。

示例：

Logger logger = new Logger();

// 日志内容 "foo" 在时刻 1 到达系统
logger.shouldPrintMessage(1, "foo"); returns true; 

// 日志内容 "bar" 在时刻 2 到达系统
logger.shouldPrintMessage(2,"bar"); returns true;

// 日志内容 "foo" 在时刻 3 到达系统
logger.shouldPrintMessage(3,"foo"); returns false;

// 日志内容 "bar" 在时刻 8 到达系统
logger.shouldPrintMessage(8,"bar"); returns false;

// 日志内容 "foo" 在时刻 10 到达系统
logger.shouldPrintMessage(10,"foo"); returns false;

// 日志内容 "foo" 在时刻 11 到达系统
logger.shouldPrintMessage(11,"foo"); returns true;

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/logger-rate-limiter
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

def __init__(self):
    self.dic = {}

def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
    if message in self.dic:
        if timestamp - self.dic[message] >= 10:
            self.dic[message] = timestamp
            return True
        else:
            return False
    else:
        self.dic[message] = timestamp
        return True




def __init__(self):
    self._msg_set = set()
    self._msg_queue = deque()

def shouldPrintMessage(self, timestamp, message):
    while self._msg_queue:
        msg, ts = self._msg_queue[0]
        if timestamp - ts >= 10:
            self._msg_queue.popleft()
            self._msg_set.remove(msg)
        else:
            break
    
    if message not in self._msg_set:
        self._msg_set.add(message)
        self._msg_queue.append((message, timestamp))
        return True
    else:
        return False
































































