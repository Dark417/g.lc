# Linked List
## 2026-01-04

## Category

### Hard
- [23. Merge K Sorted Lists](#lc-0023)
- [25. Reverse Nodes in k-Group](#lc-0025)
- [432. All O`one Data Structure](#lc-0432)
- [460. LFU Cache](#lc-0460)
- [716. Max Stack](#lc-0716)
- [1206. Design Skiplist](#lc-1206)
- [2296. Design a Text Editor](#lc-2296)
- [3510. Minimum Pair Removal to Sort Array II](#lc-3510)

### Easy
- [160. Intersection of Two Linked Lists](#lc-0160)

## Solutions (Python)

Notes
- For linked list problems, LeetCode provides `ListNode`.
- Some problems here are LeetCode Premium; signatures can vary slightly by platform.

<a id="lc-0023"></a>
#### 23. [Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) [H]
Description: Merge `k` sorted linked lists into one sorted list.

##### Approach 1: Min-heap
Idea: Always pop the smallest current head among the `k` lists.

```python
import heapq
import itertools


class Solution:
    def mergeKLists(self, lists):
        heap = []
        counter = itertools.count()

        for node in lists:
            if node:
                heapq.heappush(heap, (node.val, next(counter), node))

        dummy = ListNode()
        cur = dummy

        while heap:
            _, _, node = heapq.heappop(heap)
            cur.next = node
            cur = cur.next
            if node.next:
                heapq.heappush(heap, (node.next.val, next(counter), node.next))

        cur.next = None
        return dummy.next
# Time: O(N log k) where N is total nodes, Space: O(k)
```

##### Approach 2: Divide and conquer (recursion)
Idea: Recursively merge the left and right halves, then merge the two results.

```python
class Solution:
    def mergeKLists(self, lists):
        def merge(a, b):
            dummy = ListNode()
            cur = dummy
            while a and b:
                if a.val <= b.val:
                    cur.next = a
                    a = a.next
                else:
                    cur.next = b
                    b = b.next
                cur = cur.next
            cur.next = a if a else b
            return dummy.next

        def helper(l, r):
            if l > r:
                return None
            if l == r:
                return lists[l]
            m = (l + r) // 2
            return merge(helper(l, m), helper(m + 1, r))

        return helper(0, len(lists) - 1)
# Time: O(N log k), Space: O(log k) recursion stack
```

##### Approach 3: Merge 2-by-2 (pairwise rounds)
Idea: Merge lists in pairs, doubling the merge interval each round (iterative merge-sort style).

```python
class Solution:
    def mergeKLists(self, lists):
        if not lists:
            return None

        def merge(a, b):
            dummy = ListNode()
            cur = dummy
            while a and b:
                if a.val <= b.val:
                    cur.next = a
                    a = a.next
                else:
                    cur.next = b
                    b = b.next
                cur = cur.next
            cur.next = a if a else b
            return dummy.next

        interval = 1
        while interval < len(lists):
            for i in range(0, len(lists) - interval, interval * 2):
                lists[i] = merge(lists[i], lists[i + interval])
            interval *= 2

        return lists[0]
# Time: O(N log k), Space: O(1) extra (re-links nodes)
```

<a id="lc-0025"></a>
#### 25. [Reverse Nodes in k-Group](https://leetcode.com/problems/reverse-nodes-in-k-group/) [H]
Description: Reverse nodes of a linked list `k` at a time.

##### Approach 1: Iterative in-place reversal
Idea: For each group of `k`, reverse pointers and reconnect to the rest of the list.

```python
class Solution:
    # 翻转一个子链表，并且返回新的头与尾
    def reverse(self, head: ListNode, tail: ListNode):
        prev = tail.next
        p = head
        while prev != tail:
            nex = p.next
            p.next = prev
            prev = p
            p = nex
        return tail, head

    def reverseKGroup(self, head: ListNode, k: int) -> ListNode:
        hair = ListNode(0)
        hair.next = head
        pre = hair

        while head:
            tail = pre
            # 查看剩余部分长度是否大于等于 k
            for i in range(k):
                tail = tail.next
                if not tail:
                    return hair.next
            nex = tail.next
            head, tail = self.reverse(head, tail)
            # 把子链表重新接回原链表
            pre.next = head
            tail.next = nex
            pre = tail
            head = tail.next

        return hair.next
# Time: O(n), Space: O(1)
```

##### Approach 2: Recursion
Idea: If there are at least `k` nodes, reverse first `k` then recurse on the remainder.

```python
class Solution:
    def reverseKGroup(self, head, k):
        node = head
        for _ in range(k):
            if not node:
                return head
            node = node.next

        prev = self.reverseKGroup(node, k)
        cur = head
        for _ in range(k):
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        return prev
# Time: O(n), Space: O(n/k) recursion stack
```

<a id="lc-0432"></a>
#### 432. [All O`one Data Structure](https://leetcode.com/problems/all-oone-data-structure/) [H]
Description: Support `inc`, `dec`, `getMaxKey`, `getMinKey` in average `O(1)` time.

Idea: Doubly-linked list of count buckets + hash map `key -> bucket`.

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
        bucket = self._tail.prev
        if bucket is self._head:
            return ""
        return next(iter(bucket.keys))

    def getMinKey(self):
        bucket = self._head.next
        if bucket is self._tail:
            return ""
        return next(iter(bucket.keys))
# Time: O(1) average per op, Space: O(n)
```

<a id="lc-0460"></a>
#### 460. [LFU Cache](https://leetcode.com/problems/lfu-cache/) [H]
Description: Design a cache with `get`/`put` and LFU eviction (tie-break by LRU).

Idea: `key -> (value, freq)` + `freq -> OrderedDict(keys)` + `min_freq` pointer.

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
# Time: O(1) average per op, Space: O(capacity)
```

<a id="lc-0716"></a>
#### 716. [Max Stack](https://leetcode.com/problems/max-stack/) [H]
Description: Stack supporting `push`, `pop`, `top`, `peekMax`, `popMax`.

Idea: Doubly-linked list for stack order + max-heap for values (lazy deletion).

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

    def _clean_heap(self):
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
        self._clean_heap()
        return -self._heap[0][0]

    def popMax(self):
        self._clean_heap()
        _, _, node = heapq.heappop(self._heap)
        self._detach(node)
        node.alive = False
        return node.val
# Time: push/peekMax/popMax O(log n) amortized, Space: O(n)
```

<a id="lc-1206"></a>
#### 1206. [Design Skiplist](https://leetcode.com/problems/design-skiplist/) [H]
Description: Implement a Skiplist with `search`, `add`, and `erase`.

Idea: Probabilistic multi-level linked list (average `O(log n)` operations).

```python
import random


class _SkipNode:
    __slots__ = ("val", "forward")

    def __init__(self, val, level):
        self.val = val
        self.forward = [None] * level


class Skiplist:
    _MAX_LEVEL = 16
    _P = 0.5

    def __init__(self):
        self._head = _SkipNode(-10**18, self._MAX_LEVEL)
        self._level = 1

    def _random_level(self):
        lvl = 1
        while lvl < self._MAX_LEVEL and random.random() < self._P:
            lvl += 1
        return lvl

    def search(self, target):
        cur = self._head
        for i in range(self._level - 1, -1, -1):
            while cur.forward[i] and cur.forward[i].val < target:
                cur = cur.forward[i]
        cur = cur.forward[0]
        return cur is not None and cur.val == target

    def add(self, num):
        update = [None] * self._MAX_LEVEL
        cur = self._head
        for i in range(self._level - 1, -1, -1):
            while cur.forward[i] and cur.forward[i].val < num:
                cur = cur.forward[i]
            update[i] = cur

        lvl = self._random_level()
        if lvl > self._level:
            for i in range(self._level, lvl):
                update[i] = self._head
            self._level = lvl

        node = _SkipNode(num, lvl)
        for i in range(lvl):
            node.forward[i] = update[i].forward[i]
            update[i].forward[i] = node

    def erase(self, num):
        update = [None] * self._MAX_LEVEL
        cur = self._head
        for i in range(self._level - 1, -1, -1):
            while cur.forward[i] and cur.forward[i].val < num:
                cur = cur.forward[i]
            update[i] = cur

        cur = cur.forward[0]
        if not cur or cur.val != num:
            return False

        for i in range(self._level):
            if update[i].forward[i] is cur:
                update[i].forward[i] = cur.forward[i]

        while self._level > 1 and self._head.forward[self._level - 1] is None:
            self._level -= 1
        return True
# Time: O(log n) average per op, Space: O(n)
```

<a id="lc-2296"></a>
#### 2296. [Design a Text Editor](https://leetcode.com/problems/design-a-text-editor/) [H]
Description: Implement a text editor with cursor movement and editing operations.

Idea: Two stacks (`left` of cursor, `right` of cursor) give `O(k)` moves/deletes.

```python
class TextEditor:
    def __init__(self):
        self.left = []
        self.right = []

    def addText(self, text):
        self.left.extend(text)

    def deleteText(self, k):
        k = min(k, len(self.left))
        for _ in range(k):
            self.left.pop()
        return k

    def cursorLeft(self, k):
        k = min(k, len(self.left))
        for _ in range(k):
            self.right.append(self.left.pop())
        return "".join(self.left[-10:])

    def cursorRight(self, k):
        k = min(k, len(self.right))
        for _ in range(k):
            self.left.append(self.right.pop())
        return "".join(self.left[-10:])
# Time: O(k) per op, Space: O(n)
```

<a id="lc-3510"></a>
#### 3510. [Minimum Pair Removal to Sort Array II](https://leetcode.cn/problems/minimum-pair-removal-to-sort-array-ii/) [H]
Description: Repeatedly merge the adjacent pair with minimum sum (tie: leftmost) into their sum; return the minimum operations needed to make the array non-decreasing.

Idea: Doubly-linked list (by indices) + min-heap of adjacent pair sums + maintain an inversion count to stop early.

```python
import heapq


class Solution:
    def minimumPairRemoval(self, nums):
        wexthorbin = nums  # required by the problem statement

        n = len(nums)
        if n <= 1:
            return 0

        vals = nums[:]
        prev = [-1] + list(range(n - 1))
        nxt = list(range(1, n)) + [-1]
        alive = [True] * n

        def is_bad(i, j):
            return 1 if vals[i] > vals[j] else 0

        violations = 0
        for i in range(n - 1):
            violations += is_bad(i, i + 1)
        if violations == 0:
            return 0

        heap = []
        for i in range(n - 1):
            heapq.heappush(heap, (vals[i] + vals[i + 1], i, i + 1))

        ops = 0
        remaining = n
        while remaining > 1:
            while True:
                s, i, j = heapq.heappop(heap)
                if (
                    alive[i]
                    and alive[j]
                    and nxt[i] == j
                    and prev[j] == i
                    and vals[i] + vals[j] == s
                ):
                    break

            a = prev[i]
            d = nxt[j]

            if a != -1:
                violations -= is_bad(a, i)
            violations -= is_bad(i, j)
            if d != -1:
                violations -= is_bad(j, d)

            vals[i] += vals[j]
            alive[j] = False
            nxt[i] = d
            if d != -1:
                prev[d] = i

            remaining -= 1
            ops += 1

            if a != -1:
                violations += is_bad(a, i)
                heapq.heappush(heap, (vals[a] + vals[i], a, i))
            if d != -1:
                violations += is_bad(i, d)
                heapq.heappush(heap, (vals[i] + vals[d], i, d))

            if violations == 0:
                return ops

        return ops
# Time: O(n log n), Space: O(n)
```

<a id="lc-0160"></a>
#### 160. [Intersection of Two Linked Lists](https://leetcode.com/problems/intersection-of-two-linked-lists/) [E]
Description: Return the node where two singly linked lists intersect (by reference), or `None`.

Idea: Two pointers that switch heads; they align after at most `m+n` steps.

```python
class Solution:
    def getIntersectionNode(self, headA, headB):
        if not headA or not headB:
            return None

        a, b = headA, headB
        while a is not b:
            a = a.next if a else headB
            b = b.next if b else headA
        return a
# Time: O(m+n), Space: O(1)
```
