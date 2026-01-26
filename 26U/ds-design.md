# Data Structure Design
## 2026-01-25

## Category

### Easy
- [E] [155. Min Stack](#lc-0155) — Stack with O(1) push, pop, top, and getMin.
- [E] [225. Implement Stack using Queues](#lc-0225) — Use queues to implement a LIFO stack.
- [E] [232. Implement Queue using Stacks](#lc-0232) — Use stacks to implement a FIFO queue.

### Medium
- [M] [146. LRU Cache](#lc-0146) — O(1) get/put cache with least-recently-used eviction.
- [M] [208. Implement Trie (Prefix Tree)](#lc-0208) — Trie supporting insert, search, and prefix queries.
- [M] [355. Design Twitter](#lc-0355) — Simplified Twitter with post, follow, and news feed.
- [M] [380. Insert Delete GetRandom O(1)](#lc-0380) — Set with O(1) insert, delete, and random access.
- [M] [622. Design Circular Queue](#lc-0622) — Fixed-size circular queue.
- [M] [895. Maximum Frequency Stack](#lc-0895) — Stack that always pops the most frequent element.
- [M] [981. Time Based Key-Value Store](#lc-0981) — Key-value store with timestamp-based retrieval.
- [M] [1146. Snapshot Array](#lc-1146) — Array supporting O(1) snapshots and historical queries.
- [M] [1472. Design Browser History](#lc-1472) — Browser back/forward navigation.

### Hard
- [H] [295. Find Median from Data Stream](#lc-0295) — Maintain running median with two heaps.
- [H] [432. All O`one Data Structure](#lc-0432) — Inc/Dec/GetMax/GetMin all in O(1).
- [H] [460. LFU Cache](#lc-0460) — Cache with least-frequently-used eviction (tie-break by LRU).
- [H] [716. Max Stack](#lc-0716) — Stack supporting peekMax and popMax.

## Solutions (Python)

Notes
- For design problems, include the full class.
- Some problems overlap with other topic files (linkedlist.md, blind75.md); solutions here are self-contained.

### Easy

<a id="lc-0155"></a>
#### 155. [Min Stack](https://leetcode.com/problems/min-stack/) [E]
Description: Design a stack that supports push, pop, top, and retrieving the minimum element in O(1).

Idea: Keep a parallel min-stack that tracks the current minimum at each level.

```python
class MinStack:
    def __init__(self):
        self.st = []
        self.min_st = []

    def push(self, val):
        self.st.append(val)
        self.min_st.append(min(val, self.min_st[-1] if self.min_st else val))

    def pop(self):
        self.st.pop()
        self.min_st.pop()

    def top(self):
        return self.st[-1]

    def getMin(self):
        return self.min_st[-1]
# Time: O(1) per op, Space: O(n)
```

<a id="lc-0225"></a>
#### 225. [Implement Stack using Queues](https://leetcode.com/problems/implement-stack-using-queues/) [E]
Description: Implement a LIFO stack using only two queues (or one queue).

##### Approach 1: One queue (rotate on push)
Idea: After pushing to the queue, rotate all previous elements behind the new one.

```python
from collections import deque


class MyStack:
    def __init__(self):
        self.q = deque()

    def push(self, x):
        self.q.append(x)
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())

    def pop(self):
        return self.q.popleft()

    def top(self):
        return self.q[0]

    def empty(self):
        return not self.q
# Time: push O(n), others O(1), Space: O(n)
```

##### Approach 2: Two queues
Idea: On pop, move all but last element to the other queue; swap queues.

```python
from collections import deque


class MyStack:
    def __init__(self):
        self.q1 = deque()
        self.q2 = deque()

    def push(self, x):
        self.q1.append(x)

    def pop(self):
        while len(self.q1) > 1:
            self.q2.append(self.q1.popleft())
        val = self.q1.popleft()
        self.q1, self.q2 = self.q2, self.q1
        return val

    def top(self):
        val = self.pop()
        self.q1.append(val)
        return val

    def empty(self):
        return not self.q1
# Time: pop/top O(n), push O(1), Space: O(n)
```

<a id="lc-0232"></a>
#### 232. [Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) [E]
Description: Implement a FIFO queue using only two stacks.

Idea: Lazy transfer — push to `in_stack`; on pop/peek, dump `in_stack` into `out_stack` (reversing order) only when `out_stack` is empty. Amortized O(1).

```python
class MyQueue:
    def __init__(self):
        self.in_st = []
        self.out_st = []

    def push(self, x):
        self.in_st.append(x)

    def _move(self):
        if not self.out_st:
            while self.in_st:
                self.out_st.append(self.in_st.pop())

    def pop(self):
        self._move()
        return self.out_st.pop()

    def peek(self):
        self._move()
        return self.out_st[-1]

    def empty(self):
        return not self.in_st and not self.out_st
# Time: amortized O(1) per op, Space: O(n)
```

### Medium

<a id="lc-0146"></a>
#### 146. [LRU Cache](https://leetcode.com/problems/lru-cache/) [M]
Description: Design a cache with O(1) `get` and `put`, evicting the least-recently-used key when full.

Idea: Hash map `key -> node` + doubly-linked list ordered by recency.

```python
class _Node:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = {}
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_front(node)
        return node.val

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._add_front(node)
            return
        node = _Node(key, value)
        self.cache[key] = node
        self._add_front(node)
        if len(self.cache) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
# Time: O(1) per op, Space: O(capacity)
```

<a id="lc-0208"></a>
#### 208. [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) [M]
Description: Implement a trie supporting insert, search, and prefix queries.

Idea: Each node stores a dict `char -> child` and an `end` flag.

```python
class TrieNode:
    __slots__ = ("children", "end")

    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.end = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.end

    def startsWith(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
# Time: O(L) per op where L is word length, Space: O(total_chars)
```

<a id="lc-0355"></a>
#### 355. [Design Twitter](https://leetcode.com/problems/design-twitter/) [M]
Description: Design a simplified Twitter with postTweet, getNewsFeed (10 most recent), follow, and unfollow.

Idea: Per-user tweet list + follow set; merge k sorted lists (heap) for the feed.

```python
import heapq
from collections import defaultdict


class Twitter:
    def __init__(self):
        self.time = 0
        self.tweets = defaultdict(list)   # userId -> [(time, tweetId)]
        self.follows = defaultdict(set)   # userId -> set of followeeIds

    def postTweet(self, userId, tweetId):
        self.tweets[userId].append((self.time, tweetId))
        self.time -= 1  # negative so max-heap via heapq

    def getNewsFeed(self, userId):
        heap = []
        self.follows[userId].add(userId)
        for uid in self.follows[userId]:
            tw = self.tweets[uid]
            if tw:
                i = len(tw) - 1
                t, tid = tw[i]
                heap.append((t, tid, uid, i))
        heapq.heapify(heap)

        res = []
        while heap and len(res) < 10:
            t, tid, uid, i = heapq.heappop(heap)
            res.append(tid)
            if i > 0:
                i -= 1
                nt, ntid = self.tweets[uid][i]
                heapq.heappush(heap, (nt, ntid, uid, i))
        return res

    def follow(self, followerId, followeeId):
        self.follows[followerId].add(followeeId)

    def unfollow(self, followerId, followeeId):
        self.follows[followerId].discard(followeeId)
# Time: getNewsFeed O(k log k) where k = followees, others O(1), Space: O(users + tweets)
```

<a id="lc-0380"></a>
#### 380. [Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/) [M]
Description: Design a set supporting O(1) insert, remove, and getRandom.

Idea: Array for values + hash map `val -> index`; on remove, swap with last element.

```python
import random


class RandomizedSet:
    def __init__(self):
        self.vals = []
        self.idx = {}

    def insert(self, val):
        if val in self.idx:
            return False
        self.idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val):
        if val not in self.idx:
            return False
        i = self.idx[val]
        last = self.vals[-1]
        self.vals[i] = last
        self.idx[last] = i
        self.vals.pop()
        del self.idx[val]
        return True

    def getRandom(self):
        return random.choice(self.vals)
# Time: O(1) per op, Space: O(n)
```

<a id="lc-0622"></a>
#### 622. [Design Circular Queue](https://leetcode.com/problems/design-circular-queue/) [M]
Description: Implement a fixed-size circular queue.

Idea: Array + head index + element count.

```python
class MyCircularQueue:
    def __init__(self, k):
        self.k = k
        self.q = [0] * k
        self.head = 0
        self.cnt = 0

    def enQueue(self, value):
        if self.isFull():
            return False
        self.q[(self.head + self.cnt) % self.k] = value
        self.cnt += 1
        return True

    def deQueue(self):
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % self.k
        self.cnt -= 1
        return True

    def Front(self):
        return -1 if self.isEmpty() else self.q[self.head]

    def Rear(self):
        return -1 if self.isEmpty() else self.q[(self.head + self.cnt - 1) % self.k]

    def isEmpty(self):
        return self.cnt == 0

    def isFull(self):
        return self.cnt == self.k
# Time: O(1) per op, Space: O(k)
```

<a id="lc-0895"></a>
#### 895. [Maximum Frequency Stack](https://leetcode.com/problems/maximum-frequency-stack/) [M]
Description: Design a stack that always pops the element with the highest frequency (tie-break: most recent push).

Idea: Track `val -> freq` and `freq -> stack of vals`; maintain `max_freq`.

```python
from collections import defaultdict


class FreqStack:
    def __init__(self):
        self.freq = defaultdict(int)
        self.group = defaultdict(list)  # freq -> stack
        self.max_freq = 0

    def push(self, val):
        self.freq[val] += 1
        f = self.freq[val]
        self.max_freq = max(self.max_freq, f)
        self.group[f].append(val)

    def pop(self):
        val = self.group[self.max_freq].pop()
        self.freq[val] -= 1
        if not self.group[self.max_freq]:
            self.max_freq -= 1
        return val
# Time: O(1) per op, Space: O(n)
```

<a id="lc-0981"></a>
#### 981. [Time Based Key-Value Store](https://leetcode.com/problems/time-based-key-value-store/) [M]
Description: Key-value store where each key has timestamped values; get returns the value at the largest timestamp <= given timestamp.

Idea: Hash map `key -> sorted list of (timestamp, value)`; binary search on get.

```python
from collections import defaultdict
from bisect import bisect_right


class TimeMap:
    def __init__(self):
        self.d = defaultdict(list)  # key -> [(timestamp, value)]

    def set(self, key, value, timestamp):
        self.d[key].append((timestamp, value))

    def get(self, key, timestamp):
        arr = self.d[key]
        i = bisect_right(arr, (timestamp, chr(127))) - 1
        return arr[i][1] if i >= 0 else ""
# Time: set O(1), get O(log n), Space: O(n)
```

<a id="lc-1146"></a>
#### 1146. [Snapshot Array](https://leetcode.com/problems/snapshot-array/) [M]
Description: Implement an array that supports O(1) snapshots and historical value queries.

Idea: Per-index list of `(snap_id, val)` pairs; binary search to find the value at a given snapshot.

```python
from bisect import bisect_right


class SnapshotArray:
    def __init__(self, length):
        self.snap_id = 0
        self.data = [[(0, 0)] for _ in range(length)]

    def set(self, index, val):
        arr = self.data[index]
        if arr[-1][0] == self.snap_id:
            arr[-1] = (self.snap_id, val)
        else:
            arr.append((self.snap_id, val))

    def snap(self):
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index, snap_id):
        arr = self.data[index]
        i = bisect_right(arr, (snap_id, float('inf'))) - 1
        return arr[i][1]
# Time: set/snap O(1), get O(log S) where S = snaps for that index, Space: O(n + total sets)
```

<a id="lc-1472"></a>
#### 1472. [Design Browser History](https://leetcode.com/problems/design-browser-history/) [M]
Description: Implement browser history with visit, back, and forward.

Idea: Two stacks — `back_st` for history, `fwd_st` for forward; visiting clears forward.

```python
class BrowserHistory:
    def __init__(self, homepage):
        self.back_st = [homepage]
        self.fwd_st = []

    def visit(self, url):
        self.back_st.append(url)
        self.fwd_st.clear()

    def back(self, steps):
        while steps > 0 and len(self.back_st) > 1:
            self.fwd_st.append(self.back_st.pop())
            steps -= 1
        return self.back_st[-1]

    def forward(self, steps):
        while steps > 0 and self.fwd_st:
            self.back_st.append(self.fwd_st.pop())
            steps -= 1
        return self.back_st[-1]
# Time: back/forward O(steps), visit O(1), Space: O(n)
```

### Hard

<a id="lc-0295"></a>
#### 295. [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) [H]
Description: Maintain a running median as numbers are added.

Idea: Two heaps — max-heap for the lower half, min-heap for the upper half; keep sizes balanced.

```python
import heapq


class MedianFinder:
    def __init__(self):
        self.small = []  # max-heap (store negatives)
        self.large = []  # min-heap

    def addNum(self, num):
        heapq.heappush(self.small, -num)
        # ensure ordering: max of small <= min of large
        if self.large and -self.small[0] > self.large[0]:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        # balance sizes: small can have at most 1 more than large
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        elif len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
# Time: O(log n) per insert, O(1) median, Space: O(n)
```

<a id="lc-0432"></a>
#### 432. [All O`one Data Structure](https://leetcode.com/problems/all-oone-data-structure/) [H]
Description: Support `inc`, `dec`, `getMaxKey`, `getMinKey` all in O(1) time.

Idea: Doubly-linked list of count buckets (each holding a set of keys) + hash map `key -> bucket`.

```python
class _Bucket:
    __slots__ = ("count", "keys", "prev", "next")

    def __init__(self, count):
        self.count = count
        self.keys = set()
        self.prev = None
        self.next = None


class AllOne:
    def __init__(self):
        self._head = _Bucket(0)
        self._tail = _Bucket(0)
        self._head.next = self._tail
        self._tail.prev = self._head
        self._key_to_bucket = {}

    def _insert_after(self, node, new_node):
        new_node.prev = node
        new_node.next = node.next
        node.next.prev = new_node
        node.next = new_node

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def inc(self, key):
        if key not in self._key_to_bucket:
            first = self._head.next
            if first is self._tail or first.count != 1:
                first = _Bucket(1)
                self._insert_after(self._head, first)
            first.keys.add(key)
            self._key_to_bucket[key] = first
            return

        cur = self._key_to_bucket[key]
        nxt = cur.next
        if nxt is self._tail or nxt.count != cur.count + 1:
            nxt = _Bucket(cur.count + 1)
            self._insert_after(cur, nxt)
        nxt.keys.add(key)
        self._key_to_bucket[key] = nxt
        cur.keys.remove(key)
        if not cur.keys:
            self._remove(cur)

    def dec(self, key):
        if key not in self._key_to_bucket:
            return
        cur = self._key_to_bucket[key]
        if cur.count == 1:
            del self._key_to_bucket[key]
            cur.keys.remove(key)
            if not cur.keys:
                self._remove(cur)
            return

        prev = cur.prev
        if prev is self._head or prev.count != cur.count - 1:
            prev = _Bucket(cur.count - 1)
            self._insert_after(cur.prev, prev)
        prev.keys.add(key)
        self._key_to_bucket[key] = prev
        cur.keys.remove(key)
        if not cur.keys:
            self._remove(cur)

    def getMaxKey(self):
        b = self._tail.prev
        return next(iter(b.keys)) if b is not self._head else ""

    def getMinKey(self):
        b = self._head.next
        return next(iter(b.keys)) if b is not self._tail else ""
# Time: O(1) per op, Space: O(n)
```

<a id="lc-0460"></a>
#### 460. [LFU Cache](https://leetcode.com/problems/lfu-cache/) [H]
Description: Design a cache with O(1) `get`/`put` and least-frequently-used eviction (tie-break by LRU).

Idea: `key -> (val, freq)` maps + `freq -> OrderedDict(keys)` for LRU ordering within each frequency + `min_freq` pointer.

```python
from collections import OrderedDict, defaultdict


class LFUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.key_to_val = {}
        self.key_to_freq = {}
        self.freq_to_keys = defaultdict(OrderedDict)
        self.min_freq = 0

    def _touch(self, key):
        freq = self.key_to_freq[key]
        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq]:
            del self.freq_to_keys[freq]
            if self.min_freq == freq:
                self.min_freq += 1
        self.key_to_freq[key] = freq + 1
        self.freq_to_keys[freq + 1][key] = None

    def get(self, key):
        if key not in self.key_to_val:
            return -1
        self._touch(key)
        return self.key_to_val[key]

    def put(self, key, value):
        if self.cap == 0:
            return
        if key in self.key_to_val:
            self.key_to_val[key] = value
            self._touch(key)
            return
        if len(self.key_to_val) == self.cap:
            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_val[evict_key]
            del self.key_to_freq[evict_key]
            if not self.freq_to_keys[self.min_freq]:
                del self.freq_to_keys[self.min_freq]
        self.key_to_val[key] = value
        self.key_to_freq[key] = 1
        self.freq_to_keys[1][key] = None
        self.min_freq = 1
# Time: O(1) per op, Space: O(capacity)
```

<a id="lc-0716"></a>
#### 716. [Max Stack](https://leetcode.com/problems/max-stack/) [H]
Description: Stack supporting `push`, `pop`, `top`, `peekMax`, and `popMax`.

Idea: Doubly-linked list for stack order + max-heap for values; lazy deletion with an `alive` flag per node.

```python
import heapq


class _Node:
    __slots__ = ("val", "id", "prev", "next", "alive")

    def __init__(self, val, id_):
        self.val = val
        self.id = id_
        self.prev = None
        self.next = None
        self.alive = True


class MaxStack:
    def __init__(self):
        self._head = _Node(0, -1)
        self._tail = _Node(0, -1)
        self._head.next = self._tail
        self._tail.prev = self._head
        self._heap = []  # (-val, -id, node)
        self._id = 0

    def _append(self, node):
        last = self._tail.prev
        last.next = node
        node.prev = last
        node.next = self._tail
        self._tail.prev = node

    def _detach(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _clean(self):
        while self._heap and not self._heap[0][2].alive:
            heapq.heappop(self._heap)

    def push(self, x):
        node = _Node(x, self._id)
        self._id += 1
        self._append(node)
        heapq.heappush(self._heap, (-x, -node.id, node))

    def pop(self):
        node = self._tail.prev
        self._detach(node)
        node.alive = False
        return node.val

    def top(self):
        return self._tail.prev.val

    def peekMax(self):
        self._clean()
        return -self._heap[0][0]

    def popMax(self):
        self._clean()
        _, _, node = heapq.heappop(self._heap)
        self._detach(node)
        node.alive = False
        return node.val
# Time: push/peekMax/popMax O(log n) amortized, Space: O(n)
```
