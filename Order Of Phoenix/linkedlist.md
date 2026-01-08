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


### Medium

- [146. LRU Cache](#lc-0146)
- [2. Add Two Numbers](#lc-0002)
- [143. Reorder List](#lc-0143)
- [19. Remove Nth Node From End of List](#lc-0019)
- [148. Sort List](#lc-0148)
- [92. Reverse Linked List II](#lc-0092)
- [707. Design Linked List](#lc-0707)
- [142. Linked List Cycle II](#lc-0142)
- [138. Copy List with Random Pointer](#lc-0138)
- [24. Swap Nodes in Pairs](#lc-0024)
- [82. Remove Duplicates from Sorted List II](#lc-0082)
- [114. Flatten Binary Tree to Linked List](#lc-0114)
- [86. Partition List](#lc-0086)
- [445. Add Two Numbers II](#lc-0445)
- [61. Rotate List](#lc-0061)
- [622. Design Circular Queue](#lc-0622)
- [116. Populating Next Right Pointers in Each Node](#lc-0116)


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

<a id="lc-0146"></a>
#### 146. [LRU Cache](https://leetcode.com/problems/lru-cache/) [M]
Description: Design a cache that supports `get` and `put` in `O(1)`.

Idea: Hash map + doubly-linked list (most-recent at the front).

```python
class _Node:
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

<a id="lc-0002"></a>
#### 2. [Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) [M]
Description: Add two numbers represented by reverse-order linked lists.

Idea: Digit-by-digit addition with carry.

```python

class Solution:
    # l1 和 l2 为当前遍历的节点，carry 为进位
    # add extra parameter 'carry'!
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode], carry=0) -> Optional[ListNode]:
        if l1 is None and l2 is None and carry == 0:  # 递归边界
            return None

        s = carry
        if l1:
            s += l1.val  # 累加进位与节点值
            l1 = l1.next
        if l2:
            s += l2.val
            l2 = l2.next

        # s 除以 10 的余数为当前节点值，商为进位
        return ListNode(s % 10, self.addTwoNumbers(l1, l2, s // 10))


class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        cur = dummy = ListNode()
        carry = 0
        while l1 or l2 or carry:
            if l1:
                carry += l1.val
                l1 = l1.next
            if l2:
                carry += l2.val
                l2 = l2.next
            cur.next = ListNode(carry % 10)
            carry //= 10
            cur = cur.next
        return dummy.next
        


class Solution:
    # l1 和 l2 为当前遍历的节点，carry 为进位
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode], carry=0) -> Optional[ListNode]:
        if l1 is None and l2 is None:  # 递归边界
            return ListNode(carry) if carry else None  # 如果进位了，就额外创建一个节点
        if l1 is None:  # 如果 l1 是空的，那么此时 l2 一定不是空节点
            l1, l2 = l2, l1  # 交换 l1 与 l2，保证 l1 非空，从而简化代码
        s = carry + l1.val + (l2.val if l2 else 0)  # 节点值和进位加在一起
        l1.val = s % 10  # 每个节点保存一个数位（直接修改原链表）
        l1.next = self.addTwoNumbers(l1.next, l2.next if l2 else None, s // 10)  # 进位
        return l1


```

<a id="lc-0143"></a>
#### 143. [Reorder List](https://leetcode.com/problems/reorder-list/) [M]
Description: Reorder `L0→L1→…→Ln` to `L0→Ln→L1→Ln-1→…` (in-place).

Idea: Find middle, reverse second half, then merge two halves.

```python

# get the middle node
# slow, fast pointers
# reverse the second half
# 1 4 2 3, 2 3 not touched
class Solution:
    # 876. 链表的中间结点
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        return slow

    # 206. 反转链表
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        pre, cur = None, head
        while cur:
            nxt = cur.next
            cur.next = pre
            pre = cur
            cur = nxt
        return pre

    def reorderList(self, head: Optional[ListNode]) -> None:
        mid = self.middleNode(head)
        head2 = self.reverseList(mid)
        while head2.next:
            nxt = head.next
            nxt2 = head2.next
            head.next = head2
            head2.next = nxt
            head = nxt
            head2 = nxt2

class Solution:
    def reorderList(self, head):
        if not head or not head.next:
            return

        slow = fast = head
        while fast.next and fast.next.next:
            slow = slow.next
            fast = fast.next.next

        prev = None
        cur = slow.next
        slow.next = None
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt

        first, second = head, prev
        while second:
            n1, n2 = first.next, second.next
            first.next = second
            second.next = n1
            first, second = n1, n2
# Time: O(n), Space: O(1)
```

<a id="lc-0019"></a>
#### 19. [Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) [M]
Description: Remove the `n`th node from the end of the list.

Idea: Two pointers with a fixed gap of `n`.

```python
class Solution:
    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0)
        dummy.next = head

        fast = dummy
        for _ in range(n):
            fast = fast.next

        slow = dummy
        while fast.next:
            fast = fast.next
            slow = slow.next

        slow.next = slow.next.next
        return dummy.next
# Time: O(n), Space: O(1)


def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
    def getLength(head: ListNode) -> int:
        length = 0
        while head:
            length += 1
            head = head.next
        return length
    
    dummy = ListNode(0, head)
    length = getLength(head)
    cur = dummy
    for i in range(1, length - n + 1):
        cur = cur.next
    cur.next = cur.next.next
    return dummy.next

def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
    dummy = ListNode(0, head)
    stack = list()
    cur = dummy
    while cur:
        stack.append(cur)
        cur = cur.next
    
    for i in range(n):
        stack.pop()

    prev = stack[-1]
    prev.next = prev.next.next
    return dummy.next
```


2095. Delete the Middle Node of a Linked List
```python
class Solution:
    def deleteMiddle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        dummy = cur = ListNode(next = head)
        while cur.next != slow:
            cur = cur.next
        cur.next = cur.next.next
        return dummy.next
```

1721. Swapping Nodes in a Linked
```python
class Solution:
    def swapNodes(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        cur = head
        for _ in range(k - 1):
            cur = cur.next
        p1 = cur
        p2 = head
        cur = p1
        while cur.next:
            cur = cur.next
            p2 = p2.next
        p1.val, p2.val = p2.val, p1.val
        return head
```

<a id="lc-0148"></a>
#### 148. [Sort List](https://leetcode.com/problems/sort-list/) [M]
Description: Sort a linked list in `O(n log n)` time.

Idea: Merge sort on linked list (split by slow/fast pointers).

```python
class Solution:
    def sortList(self, head):
        if not head or not head.next:
            return head

        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        mid = slow.next
        slow.next = None

        left = self.sortList(head)
        right = self.sortList(mid)
        return self._merge(left, right)

    def _merge(self, a, b):
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
# Time: O(n log n), Space: O(log n) recursion

class Solution:
    def sortList(self, head: ListNode) -> ListNode:
        if not head or not head.next: return head # termination.
        # cut the LinkedList at the mid index.
        slow, fast = head, head.next
        while fast and fast.next:
            fast, slow = fast.next.next, slow.next
        mid, slow.next = slow.next, None # save and cut.
        # recursive for cutting.
        left, right = self.sortList(head), self.sortList(mid)
        # merge `left` and `right` linked list and return it.
        h = res = ListNode(0)
        while left and right:
            if left.val < right.val: h.next, left = left, left.next
            else: h.next, right = right, right.next
            h = h.next
        h.next = left if left else right
        return res.next

```

<a id="lc-0092"></a>
#### 92. [Reverse Linked List II](https://leetcode.com/problems/reverse-linked-list-ii/) [M]
Description: Reverse the nodes between positions `left` and `right`.

Idea: Fix the node before `left`, then do head-insertion for the sublist.

```python
class Solution:
    def reverseBetween(self, head, left, right):
        if not head or left == right:
            return head

        dummy = ListNode(0)
        dummy.next = head

        prev = dummy
        for _ in range(left - 1):
            prev = prev.next

        cur = prev.next
        for _ in range(right - left):
            move = cur.next
            cur.next = move.next
            move.next = prev.next
            prev.next = move

        return dummy.next
# Time: O(n), Space: O(1)

class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        p0 = dummy = ListNode(next=head)
        for _ in range(left - 1):
            p0 = p0.next

        pre = None
        cur = p0.next
        for _ in range(right - left + 1):
            nxt = cur.next
            cur.next = pre  # 每次循环只修改一个 next，方便大家理解
            pre = cur
            cur = nxt

        # 见视频
        p0.next.next = cur  # 1.next => 2,  2.next => 5
        p0.next = pre       # 1.next => 4
        return dummy.next
```

<a id="lc-0707"></a>
#### 707. [Design Linked List](https://leetcode.com/problems/design-linked-list/) [M]
Description: Implement a linked list with common operations.

Idea: Doubly-linked list with head/tail sentinels + size.

```python
class _Node:
    def __init__(self, val=0):
        self.val = val
        self.prev = None
        self.next = None


class MyLinkedList:
    def __init__(self):
        self.size = 0
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _node_at(self, index):
        if index < 0 or index >= self.size:
            return None

        if index < self.size // 2:
            cur = self.head.next
            for _ in range(index):
                cur = cur.next
            return cur

        cur = self.tail.prev
        for _ in range(self.size - index - 1):
            cur = cur.prev
        return cur

    def _insert_before(self, node, new_node):
        prev = node.prev
        new_node.prev = prev
        new_node.next = node
        prev.next = new_node
        node.prev = new_node

    def get(self, index):
        node = self._node_at(index)
        return node.val if node else -1

    def addAtHead(self, val):
        self._insert_before(self.head.next, _Node(val))
        self.size += 1

    def addAtTail(self, val):
        self._insert_before(self.tail, _Node(val))
        self.size += 1

    def addAtIndex(self, index, val):
        if index <= 0:
            self.addAtHead(val)
            return
        if index == self.size:
            self.addAtTail(val)
            return
        if index > self.size:
            return

        node = self._node_at(index)
        self._insert_before(node, _Node(val))
        self.size += 1

    def deleteAtIndex(self, index):
        node = self._node_at(index)
        if not node:
            return
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
# Time: O(n) per op (traversal), Space: O(n)
```

<a id="lc-0142"></a>
#### 142. [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) [M]
Description: Return the node where the cycle begins, or `None`.

Idea: Floyd's cycle detection; then reset one pointer to head.

```python
class Solution:
    def detectCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                p = head
                while p is not slow:
                    p = p.next
                    slow = slow.next
                return p
        return None
# Time: O(n), Space: O(1)
```

<a id="lc-0138"></a>
#### 138. [Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/) [M]
Description: Deep copy a list where each node has `next` and `random`.

Idea: Hash map from old nodes to new nodes (two passes).

```python
class Solution:
    def copyRandomList(self, head):
        if not head:
            return None

        old_to_new = {}
        cur = head
        while cur:
            old_to_new[cur] = Node(cur.val)
            cur = cur.next

        cur = head
        while cur:
            node = old_to_new[cur]
            node.next = old_to_new.get(cur.next)
            node.random = old_to_new.get(cur.random)
            cur = cur.next

        return old_to_new[head]
# Time: O(n), Space: O(n)
```

<a id="lc-0024"></a>
#### 24. [Swap Nodes in Pairs](https://leetcode.com/problems/swap-nodes-in-pairs/) [M]
Description: Swap every two adjacent nodes.

Idea: Iteratively swap pairs using a dummy head.

```python
class Solution:
    def swapPairs(self, head):
        dummy = ListNode(0)
        dummy.next = head
        prev = dummy

        while prev.next and prev.next.next:
            a = prev.next
            b = a.next
            prev.next = b
            a.next = b.next
            b.next = a
            prev = a

        return dummy.next
# Time: O(n), Space: O(1)
```

<a id="lc-0082"></a>
#### 82. [Remove Duplicates from Sorted List II](https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/) [M]
Description: Remove all nodes that have duplicate numbers (leave only distinct).

Idea: Use a dummy head and skip runs of duplicates.

```python
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        cur = dummy = ListNode(next=head)
        while cur.next and cur.next.next:
            val = cur.next.val
            if cur.next.next.val == val:  # 后两个节点值相同
                # 值等于 val 的节点全部删除
                while cur.next and cur.next.val == val:
                    cur.next = cur.next.next
            else:
                cur = cur.next
        return dummy.next


class Solution:
    def deleteDuplicates(self, head):
        dummy = ListNode(0)
        dummy.next = head

        prev = dummy
        cur = head
        while cur:
            if cur.next and cur.val == cur.next.val:
                dup = cur.val
                while cur and cur.val == dup:
                    cur = cur.next
                prev.next = cur
            else:
                prev = cur
                cur = cur.next

        return dummy.next
# Time: O(n), Space: O(1)
```

<a id="lc-0114"></a>
#### 114. [Flatten Binary Tree to Linked List](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/) [M]
Description: Flatten the tree to a linked list in-place (preorder).

Idea: Preorder traversal with a stack; rewire `right` pointers.

```python
class Solution:
    def flatten(self, root):
        if not root:
            return

        stack = [root]
        prev = None

        while stack:
            node = stack.pop()
            if prev:
                prev.left = None
                prev.right = node

            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)

            prev = node
# Time: O(n), Space: O(n)
```

<a id="lc-0086"></a>
#### 86. [Partition List](https://leetcode.com/problems/partition-list/) [M]
Description: Partition the list around `x` preserving relative order.

Idea: Build two lists (`< x` and `>= x`) then concatenate.

```python
class Solution:
    def partition(self, head, x):
        small_dummy = ListNode()
        big_dummy = ListNode()
        small, big = small_dummy, big_dummy

        while head:
            nxt = head.next
            head.next = None
            if head.val < x:
                small.next = head
                small = small.next
            else:
                big.next = head
                big = big.next
            head = nxt

        small.next = big_dummy.next
        return small_dummy.next
# Time: O(n), Space: O(1)
```

<a id="lc-0445"></a>
#### 445. [Add Two Numbers II](https://leetcode.com/problems/add-two-numbers-ii/) [M]
Description: Add two numbers represented by forward-order linked lists.

Idea: Use stacks to add from least-significant digit.

```python
class Solution:
    def addTwoNumbers(self, l1, l2):
        s1, s2 = [], []
        while l1:
            s1.append(l1.val)
            l1 = l1.next
        while l2:
            s2.append(l2.val)
            l2 = l2.next

        carry = 0
        head = None
        while s1 or s2 or carry:
            v1 = s1.pop() if s1 else 0
            v2 = s2.pop() if s2 else 0
            s = v1 + v2 + carry
            carry = s // 10

            node = ListNode(s % 10)
            node.next = head
            head = node

        return head
# Time: O(m+n), Space: O(m+n)
```

<a id="lc-0061"></a>
#### 61. [Rotate List](https://leetcode.com/problems/rotate-list/) [M]
Description: Rotate the list to the right by `k` places.

Idea: Make a cycle, then break it at the new tail.

```python
class Solution:
    def rotateRight(self, head, k):
        if not head or not head.next or k == 0:
            return head

        n = 1
        tail = head
        while tail.next:
            tail = tail.next
            n += 1

        k %= n
        if k == 0:
            return head

        tail.next = head
        steps = n - k
        cur = head
        for _ in range(steps - 1):
            cur = cur.next

        new_head = cur.next
        cur.next = None
        return new_head
# Time: O(n), Space: O(1)
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
        self.count = 0

    def enQueue(self, value):
        if self.isFull():
            return False
        idx = (self.head + self.count) % self.k
        self.q[idx] = value
        self.count += 1
        return True

    def deQueue(self):
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % self.k
        self.count -= 1
        return True

    def Front(self):
        if self.isEmpty():
            return -1
        return self.q[self.head]

    def Rear(self):
        if self.isEmpty():
            return -1
        return self.q[(self.head + self.count - 1) % self.k]

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == self.k
# Time: O(1) per op, Space: O(k)
```

<a id="lc-0116"></a>
#### 116. [Populating Next Right Pointers in Each Node](https://leetcode.com/problems/populating-next-right-pointers-in-each-node/) [M]
Description: Connect `next` pointers in a perfect binary tree.

Idea: Use already-built `next` pointers to traverse each level in `O(1)` extra space.

```python
class Solution:
    def connect(self, root):
        if not root:
            return None

        leftmost = root
        while leftmost.left:
            head = leftmost
            while head:
                head.left.next = head.right
                if head.next:
                    head.right.next = head.next.left
                head = head.next
            leftmost = leftmost.left

        return root
# Time: O(n), Space: O(1)
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
