# 341. 扁平化嵌套列表迭代器

def dfs(self, nests):
    for nest in nests:
        if nest.isInteger():
            self.queue.append(nest.getInteger())
        else:
            self.dfs(nest.getList())
                
def __init__(self, nestedList):
    self.queue = collections.deque()
    self.dfs(nestedList)

def next(self):
    return self.queue.popleft()

def hasNext(self):
    return len(self.queue)




def __init__(self, nestedList):
    self.stack = []
    for i in range(len(nestedList) - 1, -1, -1):
        self.stack.append(nestedList[i])
    

def next(self):
    cur = self.stack.pop()
    return cur.getInteger()

def hasNext(self):
    while self.stack:
        cur = self.stack[-1]
        if cur.isInteger():
            return True
        self.stack.pop()
        for i in range(len(cur.getList()) - 1, -1, -1):
            self.stack.append(cur.getList()[i])
    return False





def gen(nestedList):
    for ele in nestedList:
        if ele.isInteger():
            yield ele.getInteger()
        else:
            yield from gen(ele.getList())

class NestedIterator:
    def __init__(self, nestedList: [NestedInteger]):
        self.gen = gen(nestedList)
        self.stored = (False, 0)

    def next(self) -> int:
        if not self.hasNext():
            return -1
        result = self.stored[1]
        self.stored = (False, 0)
        return result

    def hasNext(self) -> bool:
        if self.stored[0]:
            return True
        try:
            self.stored = (True, next(self.gen))
            return True
        except:
            return False


















