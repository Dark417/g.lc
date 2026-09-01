```python
def binarySearch(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = l + (r - l) // 2
        if nums[m] == target:
            return m
        if nums[m] < target:
            l = m + 1
        else:
            r = m - 1
    return -1

F F F F T T T
        ^
     first true

Koko Eating Bananas
Ship Within D Days
Split Array Largest Sum
很多 binary search on answer

def firstTrue(l, r):
    while l < r:
        m = l + (r - l) // 2
        if condition(m):
            r = m
        else:
            l = m + 1
    return l

save mid
def firstTrue(l, r):
    while l <= r:
        mid = (l + r) // 2
        if feasible(mid):
            res = mid
            r = mid - 1
        else:
            l = mid + 1
    return res


T T T T F F F
      ^
   last true
def lastTrue(l, r):
    while l < r:
        m = l + (r - l + 1) // 2
        if condition(m):
            l = m
        else:
            r = m - 1
    return l


Search in Rotated Sorted Array

```

```
150
min max
define float('inf')
maxProfit
profit = p - p = 0 the same day
```

```python
import heapq
import time
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.expire_at = 0
        self.version = 0
        self.pre = None
        self.next = None

class LRUCacheTTL:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.nodes = {}
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.pre = self.head
        self.expiry_heap = []
        self.version = 0

    def remove(self, node):
        node.pre.next = node.next
        node.next.pre = node.pre

    def addFront(self, node):
        node.pre = self.head
        node.next = self.head.next
        self.head.next.pre = node
        self.head.next = node

    def purgeExpired(self):
        now = time.monotonic()
        while self.expiry_heap and self.expiry_heap[0][0] <= now:
            expire_at, version, key = heapq.heappop(self.expiry_heap)
            node = self.nodes.get(key)
            if node and node.version == version:
                self.remove(node)
                del self.nodes[key]

    def get(self, key: int) -> int:
        self.purgeExpired()
        if key not in self.nodes:
            return -1
        node = self.nodes[key]
        self.remove(node)
        self.addFront(node)
        return node.value

    def put(self, key: int, value: int, ttl: float) -> None:
        self.purgeExpired()
        self.version += 1
        expire_at = time.monotonic() + ttl
        if key in self.nodes:
            node = self.nodes[key]
            node.value = value
            node.expire_at = expire_at
            node.version = self.version
            self.remove(node)
            self.addFront(node)
        else:
            if self.capacity == 0:
                return
            if len(self.nodes) == self.capacity:
                lru = self.tail.pre
                self.remove(lru)
                del self.nodes[lru.key]
            node = Node(key, value)
            node.expire_at = expire_at
            node.version = self.version
            self.nodes[key] = node
            self.addFront(node)
        heapq.heappush(self.expiry_heap, (expire_at, self.version, key))
```

```

```
