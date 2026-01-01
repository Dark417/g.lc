# Blind 75 (NeetCode) — Questions + Python Solutions

This is the NeetCode "Blind 75" list (75 questions), grouped by category and difficulty, followed by Python reference solutions.
Problem titles/difficulty are from neetcode.io; solution writeups/code are original.

## Index (by category & difficulty)

### Arrays & Hashing
#### Easy
- [1. Two Sum](#lc-0001)
- [217. Contains Duplicate](#lc-0217)
- [242. Valid Anagram](#lc-0242)

#### Medium
- [49. Group Anagrams](#lc-0049)
- [128. Longest Consecutive Sequence](#lc-0128)
- [238. Product of Array Except Self](#lc-0238)
- [271. Encode and Decode Strings](#lc-0271)
- [347. Top K Frequent Elements](#lc-0347)

### Two Pointers
#### Easy
- [125. Valid Palindrome](#lc-0125)

#### Medium
- [11. Container With Most Water](#lc-0011)
- [15. 3Sum](#lc-0015)

### Sliding Window
#### Easy
- [121. Best Time to Buy And Sell Stock](#lc-0121)

#### Medium
- [3. Longest Substring Without Repeating Characters](#lc-0003)
- [424. Longest Repeating Character Replacement](#lc-0424)

#### Hard
- [76. Minimum Window Substring](#lc-0076)

### Stack
#### Easy
- [20. Valid Parentheses](#lc-0020)

### Binary Search
#### Medium
- [33. Search In Rotated Sorted Array](#lc-0033)
- [153. Find Minimum In Rotated Sorted Array](#lc-0153)

### Linked List
#### Easy
- [21. Merge Two Sorted Lists](#lc-0021)
- [141. Linked List Cycle](#lc-0141)
- [206. Reverse Linked List](#lc-0206)

#### Medium
- [19. Remove Nth Node From End of List](#lc-0019)
- [143. Reorder List](#lc-0143)

#### Hard
- [23. Merge K Sorted Lists](#lc-0023)

### Trees
#### Easy
- [100. Same Tree](#lc-0100)
- [104. Maximum Depth of Binary Tree](#lc-0104)
- [226. Invert Binary Tree](#lc-0226)
- [572. Subtree of Another Tree](#lc-0572)

#### Medium
- [98. Validate Binary Search Tree](#lc-0098)
- [102. Binary Tree Level Order Traversal](#lc-0102)
- [105. Construct Binary Tree From Preorder And Inorder Traversal](#lc-0105)
- [230. Kth Smallest Element In a Bst](#lc-0230)
- [235. Lowest Common Ancestor of a Binary Search Tree](#lc-0235)

#### Hard
- [124. Binary Tree Maximum Path Sum](#lc-0124)
- [297. Serialize And Deserialize Binary Tree](#lc-0297)

### Tries
#### Medium
- [208. Implement Trie Prefix Tree](#lc-0208)
- [211. Design Add And Search Words Data Structure](#lc-0211)

#### Hard
- [212. Word Search II](#lc-0212)

### Heap / Priority Queue
#### Hard
- [295. Find Median From Data Stream](#lc-0295)

### Backtracking
#### Medium
- [39. Combination Sum](#lc-0039)
- [79. Word Search](#lc-0079)

### Graphs
#### Medium
- [133. Clone Graph](#lc-0133)
- [200. Number of Islands](#lc-0200)
- [207. Course Schedule](#lc-0207)
- [261. Graph Valid Tree](#lc-0261)
- [323. Number of Connected Components In An Undirected Graph](#lc-0323)
- [417. Pacific Atlantic Water Flow](#lc-0417)

### Advanced Graphs
#### Hard
- [269. Alien Dictionary](#lc-0269)

### 1-D Dynamic Programming
#### Easy
- [70. Climbing Stairs](#lc-0070)

#### Medium
- [5. Longest Palindromic Substring](#lc-0005)
- [91. Decode Ways](#lc-0091)
- [139. Word Break](#lc-0139)
- [152. Maximum Product Subarray](#lc-0152)
- [198. House Robber](#lc-0198)
- [213. House Robber II](#lc-0213)
- [300. Longest Increasing Subsequence](#lc-0300)
- [322. Coin Change](#lc-0322)
- [647. Palindromic Substrings](#lc-0647)

### 2-D Dynamic Programming
#### Medium
- [62. Unique Paths](#lc-0062)
- [1143. Longest Common Subsequence](#lc-1143)

### Greedy
#### Medium
- [53. Maximum Subarray](#lc-0053)
- [55. Jump Game](#lc-0055)

### Intervals
#### Easy
- [252. Meeting Rooms](#lc-0252)

#### Medium
- [56. Merge Intervals](#lc-0056)
- [57. Insert Interval](#lc-0057)
- [253. Meeting Rooms II](#lc-0253)
- [435. Non Overlapping Intervals](#lc-0435)

### Math & Geometry
#### Medium
- [48. Rotate Image](#lc-0048)
- [54. Spiral Matrix](#lc-0054)
- [73. Set Matrix Zeroes](#lc-0073)

### Bit Manipulation
#### Easy
- [190. Reverse Bits](#lc-0190)
- [191. Number of 1 Bits](#lc-0191)
- [268. Missing Number](#lc-0268)
- [338. Counting Bits](#lc-0338)

#### Medium
- [371. Sum of Two Integers](#lc-0371)

## Solutions (Python)

Notes
- For linked list / tree / graph problems, LeetCode provides `ListNode`, `TreeNode`, and `Node` classes.
- Some problems are LeetCode Premium (e.g., `Graph Valid Tree`, `Meeting Rooms`, `Alien Dictionary`); signatures may vary slightly across platforms.

### Arrays & Hashing

<a id="lc-0001"></a>
#### 1. Two Sum (Easy)
LeetCode: https://leetcode.com/problems/two-sum/

- Idea: Keep a hash map `value -> index`; for each number `x`, check whether `target - x` was seen before.
- Time: `O(n)`
- Space: `O(n)`

```python
class Solution:
    def twoSum(self, nums, target):
        index = {}
        for i, x in enumerate(nums):
            need = target - x
            if need in index:
                return [index[need], i]
            index[x] = i
        return []
```

<a id="lc-0217"></a>
#### 217. Contains Duplicate (Easy)
LeetCode: https://leetcode.com/problems/contains-duplicate/

- Idea: Track seen values in a set; if we ever see one twice, return `True`.
- Time: `O(n)`
- Space: `O(n)`

```python
class Solution:
    def containsDuplicate(self, nums):
        seen = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False
```

<a id="lc-0242"></a>
#### 242. Valid Anagram (Easy)
LeetCode: https://leetcode.com/problems/valid-anagram/

- Idea: Two strings are anagrams iff their character counts match.
- Time: `O(n)`
- Space: `O(1)` for fixed alphabet, otherwise `O(k)` distinct chars

```python
from collections import Counter


class Solution:
    def isAnagram(self, s, t):
        return Counter(s) == Counter(t)
```

<a id="lc-0049"></a>
#### 49. Group Anagrams (Medium)
LeetCode: https://leetcode.com/problems/group-anagrams/

- Idea: Use a hash map keyed by a canonical signature for each word (e.g., a 26-count tuple).
- Time: `O(n * k)` where `k` is word length (counting chars)
- Space: `O(n * k)` for grouping output

```python
from collections import defaultdict


class Solution:
    def groupAnagrams(self, strs):
        groups = defaultdict(list)

        for s in strs:
            counts = [0] * 26
            for ch in s:
                counts[ord(ch) - ord("a")] += 1
            groups[tuple(counts)].append(s)

        return list(groups.values())
```

<a id="lc-0128"></a>
#### 128. Longest Consecutive Sequence (Medium)
LeetCode: https://leetcode.com/problems/longest-consecutive-sequence/

- Idea: Put everything in a set; only start counting from numbers that have no predecessor (`x-1` not in set).
- Time: `O(n)` average
- Space: `O(n)`

```python
class Solution:
    def longestConsecutive(self, nums):
        s = set(nums)
        best = 0

        for x in s:
            if x - 1 not in s:  # start of a run
                y = x
                while y in s:
                    y += 1
                best = max(best, y - x)

        return best
```

<a id="lc-0238"></a>
#### 238. Product of Array Except Self (Medium)
LeetCode: https://leetcode.com/problems/product-of-array-except-self/

- Idea: Build prefix products left-to-right into `ans`, then multiply by suffix products right-to-left.
- Time: `O(n)`
- Space: `O(1)` extra (not counting the output array)

```python
class Solution:
    def productExceptSelf(self, nums):
        n = len(nums)
        ans = [1] * n

        prefix = 1
        for i in range(n):
            ans[i] = prefix
            prefix *= nums[i]

        suffix = 1
        for i in range(n - 1, -1, -1):
            ans[i] *= suffix
            suffix *= nums[i]

        return ans
```

<a id="lc-0271"></a>
#### 271. Encode and Decode Strings (Medium)
LeetCode: https://leetcode.com/problems/encode-and-decode-strings/

- Idea: Length-prefix each string so decoding is unambiguous: `<len>#<string>...`.
- Time: `O(total_chars)` for both encode/decode
- Space: `O(total_chars)` for the encoded string / output list

```python
class Codec:
    def encode(self, strs):
        out = []
        for s in strs:
            out.append(str(len(s)))
            out.append("#")
            out.append(s)
        return "".join(out)

    def decode(self, s):
        res = []
        i = 0
        while i < len(s):
            j = i
            while s[j] != "#":
                j += 1
            length = int(s[i:j])
            j += 1
            res.append(s[j : j + length])
            i = j + length
        return res
```

<a id="lc-0347"></a>
#### 347. Top K Frequent Elements (Medium)
LeetCode: https://leetcode.com/problems/top-k-frequent-elements/

##### Approach 1: Bucket sort
- Idea: Count frequencies, then bucket numbers by frequency and scan buckets from high to low.
- Time: `O(n)`
- Space: `O(n)`

```python
from collections import Counter


class Solution:
    def topKFrequent(self, nums, k):
        freq = Counter(nums)
        buckets = [[] for _ in range(len(nums) + 1)]

        for num, c in freq.items():
            buckets[c].append(num)

        res = []
        for c in range(len(buckets) - 1, 0, -1):
            for num in buckets[c]:
                res.append(num)
                if len(res) == k:
                    return res
        return res
```

##### Approach 2: Min-heap of size `k`
- Idea: Keep only the `k` most frequent in a min-heap.
- Time: `O(n log k)`
- Space: `O(n)` for the counts + `O(k)` heap

```python
import heapq
from collections import Counter


class Solution:
    def topKFrequent(self, nums, k):
        freq = Counter(nums)
        heap = []

        for num, c in freq.items():
            heapq.heappush(heap, (c, num))
            if len(heap) > k:
                heapq.heappop(heap)

        return [num for _, num in heap]
```

### Two Pointers

<a id="lc-0125"></a>
#### 125. Valid Palindrome (Easy)
LeetCode: https://leetcode.com/problems/valid-palindrome/

- Idea: Two pointers; skip non-alphanumerics and compare lowercased characters.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def isPalindrome(self, s):
        i, j = 0, len(s) - 1

        while i < j:
            while i < j and not s[i].isalnum():
                i += 1
            while i < j and not s[j].isalnum():
                j -= 1
            if s[i].lower() != s[j].lower():
                return False
            i += 1
            j -= 1

        return True
```

<a id="lc-0011"></a>
#### 11. Container With Most Water (Medium)
LeetCode: https://leetcode.com/problems/container-with-most-water/

- Idea: Two pointers; the area is limited by the shorter wall, so move the shorter pointer inward.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def maxArea(self, height):
        l, r = 0, len(height) - 1
        best = 0

        while l < r:
            best = max(best, (r - l) * min(height[l], height[r]))
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1

        return best
```

<a id="lc-0015"></a>
#### 15. 3Sum (Medium)
LeetCode: https://leetcode.com/problems/3sum/

- Idea: Sort; fix `i`, then run a 2-sum with two pointers on `i+1..n-1`, skipping duplicates.
- Time: `O(n^2)`
- Space: `O(1)` extra (ignoring output)

```python
class Solution:
    def threeSum(self, nums):
        nums.sort()
        res = []
        n = len(nums)

        for i in range(n):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            if nums[i] > 0:
                break

            l, r = i + 1, n - 1
            while l < r:
                s = nums[i] + nums[l] + nums[r]
                if s < 0:
                    l += 1
                elif s > 0:
                    r -= 1
                else:
                    res.append([nums[i], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1

        return res
```

### Sliding Window

<a id="lc-0121"></a>
#### 121. Best Time to Buy And Sell Stock (Easy)
LeetCode: https://leetcode.com/problems/best-time-to-buy-and-sell-stock/

- Idea: Track the minimum price so far; at each day, consider selling today.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def maxProfit(self, prices):
        min_price = float("inf")
        best = 0

        for p in prices:
            min_price = min(min_price, p)
            best = max(best, p - min_price)

        return best
```

<a id="lc-0003"></a>
#### 3. Longest Substring Without Repeating Characters (Medium)
LeetCode: https://leetcode.com/problems/longest-substring-without-repeating-characters/

- Idea: Sliding window; store last seen index for each char and move `left` past duplicates.
- Time: `O(n)`
- Space: `O(k)` distinct chars in window

```python
class Solution:
    def lengthOfLongestSubstring(self, s):
        last = {}
        left = 0
        best = 0

        for right, ch in enumerate(s):
            if ch in last and last[ch] >= left:
                left = last[ch] + 1
            last[ch] = right
            best = max(best, right - left + 1)

        return best
```

<a id="lc-0424"></a>
#### 424. Longest Repeating Character Replacement (Medium)
LeetCode: https://leetcode.com/problems/longest-repeating-character-replacement/

- Idea: Sliding window; keep `max_count` of any char in the window. Window is valid if `window_size - max_count <= k`.
- Time: `O(n)`
- Space: `O(k)` distinct chars (at most alphabet size)

```python
from collections import defaultdict


class Solution:
    def characterReplacement(self, s, k):
        counts = defaultdict(int)
        left = 0
        max_count = 0
        best = 0

        for right, ch in enumerate(s):
            counts[ch] += 1
            max_count = max(max_count, counts[ch])

            while (right - left + 1) - max_count > k:
                counts[s[left]] -= 1
                left += 1

            best = max(best, right - left + 1)

        return best
```

<a id="lc-0076"></a>
#### 76. Minimum Window Substring (Hard)
LeetCode: https://leetcode.com/problems/minimum-window-substring/

- Idea: Sliding window with counts; expand right until all required chars are satisfied, then shrink left while staying valid.
- Time: `O(|s| + |t|)`
- Space: `O(k)` distinct chars in `t`

```python
from collections import Counter, defaultdict


class Solution:
    def minWindow(self, s, t):
        if not s or not t:
            return ""

        need = Counter(t)
        have = defaultdict(int)
        required = len(need)
        formed = 0

        best_len = float("inf")
        best_l = 0

        l = 0
        for r, ch in enumerate(s):
            if ch in need:
                have[ch] += 1
                if have[ch] == need[ch]:
                    formed += 1

            while formed == required and l <= r:
                if r - l + 1 < best_len:
                    best_len = r - l + 1
                    best_l = l

                left_ch = s[l]
                if left_ch in need:
                    have[left_ch] -= 1
                    if have[left_ch] < need[left_ch]:
                        formed -= 1
                l += 1

        if best_len == float("inf"):
            return ""
        return s[best_l : best_l + best_len]
```

### Stack

<a id="lc-0020"></a>
#### 20. Valid Parentheses (Easy)
LeetCode: https://leetcode.com/problems/valid-parentheses/

- Idea: Use a stack; every closing bracket must match the most recent unmatched opening bracket.
- Time: `O(n)`
- Space: `O(n)`

```python
class Solution:
    def isValid(self, s):
        stack = []
        pair = {")": "(", "]": "[", "}": "{"}

        for ch in s:
            if ch in pair:
                if not stack or stack[-1] != pair[ch]:
                    return False
                stack.pop()
            else:
                stack.append(ch)

        return not stack
```

### Binary Search

<a id="lc-0033"></a>
#### 33. Search In Rotated Sorted Array (Medium)
LeetCode: https://leetcode.com/problems/search-in-rotated-sorted-array/

- Idea: Binary search; at each step, determine which half is sorted and narrow accordingly.
- Time: `O(log n)`
- Space: `O(1)`

```python
class Solution:
    def search(self, nums, target):
        l, r = 0, len(nums) - 1

        while l <= r:
            m = (l + r) // 2
            if nums[m] == target:
                return m

            if nums[l] <= nums[m]:  # left half sorted
                if nums[l] <= target < nums[m]:
                    r = m - 1
                else:
                    l = m + 1
            else:  # right half sorted
                if nums[m] < target <= nums[r]:
                    l = m + 1
                else:
                    r = m - 1

        return -1
```

<a id="lc-0153"></a>
#### 153. Find Minimum In Rotated Sorted Array (Medium)
LeetCode: https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/

- Idea: Binary search; compare `nums[mid]` to `nums[right]` to decide which side contains the minimum.
- Time: `O(log n)`
- Space: `O(1)`

```python
class Solution:
    def findMin(self, nums):
        l, r = 0, len(nums) - 1

        while l < r:
            m = (l + r) // 2
            if nums[m] > nums[r]:
                l = m + 1
            else:
                r = m

        return nums[l]
```

### Linked List

<a id="lc-0021"></a>
#### 21. Merge Two Sorted Lists (Easy)
LeetCode: https://leetcode.com/problems/merge-two-sorted-lists/

- Idea: Two pointers + dummy head; repeatedly take the smaller node.
- Time: `O(m + n)`
- Space: `O(1)` (re-links existing nodes)

```python
class Solution:
    def mergeTwoLists(self, list1, list2):
        dummy = ListNode()
        cur = dummy

        a, b = list1, list2
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
```

<a id="lc-0141"></a>
#### 141. Linked List Cycle (Easy)
LeetCode: https://leetcode.com/problems/linked-list-cycle/

##### Approach 1: Floyd's tortoise-and-hare
- Idea: If a cycle exists, fast pointer will eventually meet slow pointer.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def hasCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False
```

##### Approach 2: Hash set
- Idea: Track visited nodes by identity.
- Time: `O(n)`
- Space: `O(n)`

```python
class Solution:
    def hasCycle(self, head):
        seen = set()
        cur = head
        while cur:
            if cur in seen:
                return True
            seen.add(cur)
            cur = cur.next
        return False
```

<a id="lc-0206"></a>
#### 206. Reverse Linked List (Easy)
LeetCode: https://leetcode.com/problems/reverse-linked-list/

##### Approach 1: Iterative
- Idea: Rewire `next` pointers while walking the list.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def reverseList(self, head):
        prev = None
        cur = head

        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt

        return prev
```

##### Approach 2: Recursive
- Idea: Reverse the rest of the list and attach current node at the end.
- Time: `O(n)`
- Space: `O(n)` recursion stack

```python
class Solution:
    def reverseList(self, head):
        def dfs(node, prev):
            if not node:
                return prev
            nxt = node.next
            node.next = prev
            return dfs(nxt, node)

        return dfs(head, None)
```

<a id="lc-0019"></a>
#### 19. Remove Nth Node From End of List (Medium)
LeetCode: https://leetcode.com/problems/remove-nth-node-from-end-of-list/

- Idea: Two pointers; move `fast` `n` steps ahead, then move both until `fast` reaches the end.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0, head)
        fast = slow = dummy

        for _ in range(n):
            fast = fast.next

        while fast and fast.next:
            fast = fast.next
            slow = slow.next

        slow.next = slow.next.next
        return dummy.next
```

<a id="lc-0143"></a>
#### 143. Reorder List (Medium)
LeetCode: https://leetcode.com/problems/reorder-list/

- Idea: Find middle, reverse second half, then weave the two lists together.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def reorderList(self, head):
        if not head or not head.next:
            return

        # 1) Find middle (slow)
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        # 2) Reverse second half (starting at slow)
        prev = None
        cur = slow
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        second = prev

        # 3) Merge / weave
        first = head
        while second.next:
            tmp1 = first.next
            tmp2 = second.next
            first.next = second
            second.next = tmp1
            first = tmp1
            second = tmp2
```

<a id="lc-0023"></a>
#### 23. Merge K Sorted Lists (Hard)
LeetCode: https://leetcode.com/problems/merge-k-sorted-lists/

##### Approach 1: Min-heap
- Idea: Always pop the smallest current head among the `k` lists.
- Time: `O(N log k)` where `N` is total nodes
- Space: `O(k)`

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
```

##### Approach 2: Divide and conquer (pairwise merging)
- Idea: Merge lists in pairs (like merge sort) until one list remains.
- Time: `O(N log k)`
- Space: `O(1)` extra (re-links nodes)

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
```

### Trees

<a id="lc-0100"></a>
#### 100. Same Tree (Easy)
LeetCode: https://leetcode.com/problems/same-tree/

- Idea: Recursively compare structure and values.
- Time: `O(n)`
- Space: `O(h)` recursion stack

```python
class Solution:
    def isSameTree(self, p, q):
        if not p and not q:
            return True
        if not p or not q or p.val != q.val:
            return False
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
```

<a id="lc-0104"></a>
#### 104. Maximum Depth of Binary Tree (Easy)
LeetCode: https://leetcode.com/problems/maximum-depth-of-binary-tree/

- Idea: Depth is `1 + max(depth(left), depth(right))`.
- Time: `O(n)`
- Space: `O(h)` recursion stack

```python
class Solution:
    def maxDepth(self, root):
        if not root:
            return 0
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))
```

<a id="lc-0226"></a>
#### 226. Invert Binary Tree (Easy)
LeetCode: https://leetcode.com/problems/invert-binary-tree/

- Idea: Swap left/right recursively.
- Time: `O(n)`
- Space: `O(h)` recursion stack

```python
class Solution:
    def invertTree(self, root):
        if not root:
            return None
        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
        return root
```

<a id="lc-0572"></a>
#### 572. Subtree of Another Tree (Easy)
LeetCode: https://leetcode.com/problems/subtree-of-another-tree/

- Idea: Traverse `root`; at each node, check if the two trees match exactly.
- Time: `O(n * m)` worst-case
- Space: `O(h)` recursion stack

```python
class Solution:
    def isSubtree(self, root, subRoot):
        def same(a, b):
            if not a and not b:
                return True
            if not a or not b or a.val != b.val:
                return False
            return same(a.left, b.left) and same(a.right, b.right)

        if not subRoot:
            return True
        if not root:
            return False
        if same(root, subRoot):
            return True
        return self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)
```

<a id="lc-0098"></a>
#### 98. Validate Binary Search Tree (Medium)
LeetCode: https://leetcode.com/problems/validate-binary-search-tree/

##### Approach 1: DFS with bounds
- Idea: Every node must lie in `(low, high)` where bounds tighten as you go down the tree.
- Time: `O(n)`
- Space: `O(h)`

```python
class Solution:
    def isValidBST(self, root):
        def dfs(node, low, high):
            if not node:
                return True
            if not (low < node.val < high):
                return False
            return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)

        return dfs(root, float("-inf"), float("inf"))
```

##### Approach 2: In-order traversal
- Idea: In-order traversal of a BST yields a strictly increasing sequence.
- Time: `O(n)`
- Space: `O(h)`

```python
class Solution:
    def isValidBST(self, root):
        stack = []
        cur = root
        prev = None

        while stack or cur:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()

            if prev is not None and cur.val <= prev:
                return False
            prev = cur.val
            cur = cur.right

        return True
```

<a id="lc-0102"></a>
#### 102. Binary Tree Level Order Traversal (Medium)
LeetCode: https://leetcode.com/problems/binary-tree-level-order-traversal/

##### Approach 1: BFS
- Idea: Use a queue; process one full level at a time.
- Time: `O(n)`
- Space: `O(n)` (queue in worst case)

```python
from collections import deque


class Solution:
    def levelOrder(self, root):
        if not root:
            return []

        res = []
        q = deque([root])

        while q:
            level = []
            for _ in range(len(q)):
                node = q.popleft()
                level.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            res.append(level)

        return res
```

##### Approach 2: DFS (collect by depth)
- Idea: DFS with a `depth` parameter; append to `res[depth]`.
- Time: `O(n)`
- Space: `O(h)`

```python
class Solution:
    def levelOrder(self, root):
        res = []

        def dfs(node, depth):
            if not node:
                return
            if depth == len(res):
                res.append([])
            res[depth].append(node.val)
            dfs(node.left, depth + 1)
            dfs(node.right, depth + 1)

        dfs(root, 0)
        return res
```

<a id="lc-0105"></a>
#### 105. Construct Binary Tree From Preorder And Inorder Traversal (Medium)
LeetCode: https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/

- Idea: Preorder picks the root first; inorder splits left/right subtrees around the root.
- Time: `O(n)` with an inorder index map
- Space: `O(n)` for the map + recursion stack

```python
class Solution:
    def buildTree(self, preorder, inorder):
        idx = {val: i for i, val in enumerate(inorder)}
        pre_i = 0

        def build(l, r):
            nonlocal pre_i
            if l > r:
                return None

            root_val = preorder[pre_i]
            pre_i += 1
            root = TreeNode(root_val)

            mid = idx[root_val]
            root.left = build(l, mid - 1)
            root.right = build(mid + 1, r)
            return root

        return build(0, len(inorder) - 1)
```

<a id="lc-0230"></a>
#### 230. Kth Smallest Element In a BST (Medium)
LeetCode: https://leetcode.com/problems/kth-smallest-element-in-a-bst/

- Idea: In-order traversal visits BST nodes in sorted order; stop at the k-th visit.
- Time: `O(h + k)` average
- Space: `O(h)`

```python
class Solution:
    def kthSmallest(self, root, k):
        stack = []
        cur = root

        while stack or cur:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            k -= 1
            if k == 0:
                return cur.val
            cur = cur.right
```

<a id="lc-0235"></a>
#### 235. Lowest Common Ancestor of a Binary Search Tree (Medium)
LeetCode: https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/

- Idea: Use BST ordering: if both targets are < node, go left; if both > node, go right; else node is LCA.
- Time: `O(h)`
- Space: `O(1)`

```python
class Solution:
    def lowestCommonAncestor(self, root, p, q):
        a, b = p.val, q.val
        cur = root

        while cur:
            if a < cur.val and b < cur.val:
                cur = cur.left
            elif a > cur.val and b > cur.val:
                cur = cur.right
            else:
                return cur
```

<a id="lc-0124"></a>
#### 124. Binary Tree Maximum Path Sum (Hard)
LeetCode: https://leetcode.com/problems/binary-tree-maximum-path-sum/

- Idea: For each node, compute the max "gain" to contribute to its parent (choose at most one side),
  while updating a global best using `node + left_gain + right_gain`.
- Time: `O(n)`
- Space: `O(h)`

```python
class Solution:
    def maxPathSum(self, root):
        best = float("-inf")

        def gain(node):
            nonlocal best
            if not node:
                return 0

            left = max(gain(node.left), 0)
            right = max(gain(node.right), 0)

            best = max(best, node.val + left + right)
            return node.val + max(left, right)

        gain(root)
        return best
```

<a id="lc-0297"></a>
#### 297. Serialize And Deserialize Binary Tree (Hard)
LeetCode: https://leetcode.com/problems/serialize-and-deserialize-binary-tree/

- Idea: Preorder DFS with a null marker (e.g., `#`) uniquely represents the tree.
- Time: `O(n)` for both serialize/deserialize
- Space: `O(n)`

```python
class Codec:
    def serialize(self, root):
        vals = []

        def dfs(node):
            if not node:
                vals.append("#")
                return
            vals.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ",".join(vals)

    def deserialize(self, data):
        vals = iter(data.split(","))

        def dfs():
            val = next(vals)
            if val == "#":
                return None
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node

        return dfs()
```

### Tries

<a id="lc-0208"></a>
#### 208. Implement Trie Prefix Tree (Medium)
LeetCode: https://leetcode.com/problems/implement-trie-prefix-tree/

- Idea: Each node stores a map of `char -> child` and an `end` flag.
- Time: `O(L)` per operation where `L` is word length
- Space: `O(total_chars)` inserted

```python
class TrieNode:
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
```

<a id="lc-0211"></a>
#### 211. Design Add And Search Words Data Structure (Medium)
LeetCode: https://leetcode.com/problems/design-add-and-search-words-data-structure/

- Idea: Trie + DFS when encountering wildcard `.` (try all children).
- Time: `O(L)` average; `O(26^L)` worst-case with many wildcards
- Space: `O(total_chars)` inserted

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False


class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True

    def search(self, word):
        def dfs(i, node):
            if i == len(word):
                return node.end

            ch = word[i]
            if ch == ".":
                return any(dfs(i + 1, child) for child in node.children.values())

            if ch not in node.children:
                return False
            return dfs(i + 1, node.children[ch])

        return dfs(0, self.root)
```

<a id="lc-0212"></a>
#### 212. Word Search II (Hard)
LeetCode: https://leetcode.com/problems/word-search-ii/

- Idea: Insert words into a trie; run DFS from each cell, walking the trie to prune impossible paths early.
- Time: Depends on branching; trie pruning makes it practical for constraints.
- Space: Trie `O(total_chars)` + recursion `O(R*C)` worst-case

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None  # store full word at terminal nodes


class Solution:
    def findWords(self, board, words):
        root = TrieNode()
        for w in words:
            node = root
            for ch in w:
                node = node.children.setdefault(ch, TrieNode())
            node.word = w

        rows, cols = len(board), len(board[0])
        res = []

        def dfs(r, c, node):
            ch = board[r][c]
            if ch not in node.children:
                return

            nxt = node.children[ch]
            if nxt.word is not None:
                res.append(nxt.word)
                nxt.word = None  # avoid duplicates

            board[r][c] = "#"
            if r > 0 and board[r - 1][c] != "#":
                dfs(r - 1, c, nxt)
            if r + 1 < rows and board[r + 1][c] != "#":
                dfs(r + 1, c, nxt)
            if c > 0 and board[r][c - 1] != "#":
                dfs(r, c - 1, nxt)
            if c + 1 < cols and board[r][c + 1] != "#":
                dfs(r, c + 1, nxt)
            board[r][c] = ch

            # prune dead branches
            if not nxt.children and nxt.word is None:
                node.children.pop(ch, None)

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)

        return res
```

### Heap / Priority Queue

<a id="lc-0295"></a>
#### 295. Find Median From Data Stream (Hard)
LeetCode: https://leetcode.com/problems/find-median-from-data-stream/

- Idea: Two heaps: max-heap for the lower half, min-heap for the upper half; keep sizes balanced.
- Time: `O(log n)` per insert, `O(1)` median
- Space: `O(n)`

```python
import heapq


class MedianFinder:
    def __init__(self):
        self.small = []  # max heap (store negatives)
        self.large = []  # min heap

    def addNum(self, num):
        heapq.heappush(self.small, -num)

        # ensure ordering property
        if self.large and (-self.small[0]) > self.large[0]:
            heapq.heappush(self.large, -heapq.heappop(self.small))

        # balance sizes
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        elif len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
```

### Backtracking

<a id="lc-0039"></a>
#### 39. Combination Sum (Medium)
LeetCode: https://leetcode.com/problems/combination-sum/

- Idea: DFS/backtracking; at each index, choose the current candidate any number of times.
- Time: Exponential in worst case (output-sensitive)
- Space: `O(target)` recursion depth

```python
class Solution:
    def combinationSum(self, candidates, target):
        candidates.sort()
        res = []

        def dfs(start, remaining, path):
            if remaining == 0:
                res.append(path[:])
                return

            for i in range(start, len(candidates)):
                c = candidates[i]
                if c > remaining:
                    break
                path.append(c)
                dfs(i, remaining - c, path)  # reuse allowed
                path.pop()

        dfs(0, target, [])
        return res
```

<a id="lc-0079"></a>
#### 79. Word Search (Medium)
LeetCode: https://leetcode.com/problems/word-search/

- Idea: Backtracking from each cell; mark visited cells in-place during the current path.
- Time: `O(R*C*4^L)` worst-case
- Space: `O(L)` recursion stack

```python
class Solution:
    def exist(self, board, word):
        rows, cols = len(board), len(board[0])

        def dfs(r, c, i):
            if i == len(word):
                return True
            if not (0 <= r < rows and 0 <= c < cols):
                return False
            if board[r][c] != word[i]:
                return False

            tmp = board[r][c]
            board[r][c] = "#"
            found = (
                dfs(r + 1, c, i + 1)
                or dfs(r - 1, c, i + 1)
                or dfs(r, c + 1, i + 1)
                or dfs(r, c - 1, i + 1)
            )
            board[r][c] = tmp
            return found

        for r in range(rows):
            for c in range(cols):
                if dfs(r, c, 0):
                    return True
        return False
```

### Graphs

<a id="lc-0133"></a>
#### 133. Clone Graph (Medium)
LeetCode: https://leetcode.com/problems/clone-graph/

##### Approach 1: DFS + hash map
- Idea: `old_node -> new_node` mapping; recursively clone neighbors.
- Time: `O(V + E)`
- Space: `O(V)`

```python
class Solution:
    def cloneGraph(self, node):
        if not node:
            return None

        clones = {}

        def dfs(cur):
            if cur in clones:
                return clones[cur]
            copy = Node(cur.val)
            clones[cur] = copy
            copy.neighbors = [dfs(nei) for nei in cur.neighbors]
            return copy

        return dfs(node)
```

##### Approach 2: BFS + hash map
- Idea: Build clones level-by-level, wiring edges as you go.
- Time: `O(V + E)`
- Space: `O(V)`

```python
from collections import deque


class Solution:
    def cloneGraph(self, node):
        if not node:
            return None

        clones = {node: Node(node.val)}
        q = deque([node])

        while q:
            cur = q.popleft()
            for nei in cur.neighbors:
                if nei not in clones:
                    clones[nei] = Node(nei.val)
                    q.append(nei)
                clones[cur].neighbors.append(clones[nei])

        return clones[node]
```

<a id="lc-0200"></a>
#### 200. Number of Islands (Medium)
LeetCode: https://leetcode.com/problems/number-of-islands/

##### Approach 1: DFS flood-fill
- Idea: For every land cell, flood-fill (turn `1` to `0`) to mark the entire island.
- Time: `O(R*C)`
- Space: `O(R*C)` recursion stack worst-case

```python
class Solution:
    def numIslands(self, grid):
        if not grid:
            return 0

        rows, cols = len(grid), len(grid[0])
        islands = 0

        def dfs(r, c):
            if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != "1":
                return
            grid[r][c] = "0"
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "1":
                    islands += 1
                    dfs(r, c)

        return islands
```

##### Approach 2: BFS flood-fill
- Idea: Same flood-fill, but iterative with a queue.
- Time: `O(R*C)`
- Space: `O(R*C)` queue worst-case

```python
from collections import deque


class Solution:
    def numIslands(self, grid):
        if not grid:
            return 0

        rows, cols = len(grid), len(grid[0])
        islands = 0
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != "1":
                    continue
                islands += 1
                grid[r][c] = "0"
                q = deque([(r, c)])

                while q:
                    x, y = q.popleft()
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == "1":
                            grid[nx][ny] = "0"
                            q.append((nx, ny))

        return islands
```

<a id="lc-0207"></a>
#### 207. Course Schedule (Medium)
LeetCode: https://leetcode.com/problems/course-schedule/

##### Approach 1: DFS cycle detection
- Idea: `0=unvisited, 1=visiting, 2=done`; finding a back-edge to `visiting` means a cycle.
- Time: `O(V + E)`
- Space: `O(V + E)`

```python
from collections import defaultdict


class Solution:
    def canFinish(self, numCourses, prerequisites):
        graph = defaultdict(list)
        for a, b in prerequisites:
            graph[a].append(b)

        UNVISITED, VISITING, DONE = 0, 1, 2
        state = [UNVISITED] * numCourses

        def dfs(course):
            if state[course] == VISITING:
                return False
            if state[course] == DONE:
                return True

            state[course] = VISITING
            for pre in graph[course]:
                if not dfs(pre):
                    return False
            state[course] = DONE
            return True

        for c in range(numCourses):
            if not dfs(c):
                return False
        return True
```

##### Approach 2: Kahn's algorithm (BFS topo sort)
- Idea: Take nodes with indegree 0; remove edges; if you can take all courses, no cycle.
- Time: `O(V + E)`
- Space: `O(V + E)`

```python
from collections import defaultdict, deque


class Solution:
    def canFinish(self, numCourses, prerequisites):
        graph = defaultdict(list)
        indeg = [0] * numCourses

        for a, b in prerequisites:
            graph[b].append(a)  # b -> a
            indeg[a] += 1

        q = deque([i for i in range(numCourses) if indeg[i] == 0])
        taken = 0

        while q:
            cur = q.popleft()
            taken += 1
            for nxt in graph[cur]:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    q.append(nxt)

        return taken == numCourses
```

<a id="lc-0261"></a>
#### 261. Graph Valid Tree (Medium)
LeetCode: https://leetcode.com/problems/graph-valid-tree/

- Idea: A valid tree has exactly `n-1` edges and no cycles. Union-Find detects cycles efficiently.
- Time: `O(n + e * α(n))`
- Space: `O(n)`

```python
class Solution:
    def validTree(self, n, edges):
        if len(edges) != n - 1:
            return False

        parent = list(range(n))
        rank = [0] * n

        def find(x):
            while x != parent[x]:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1
            return True

        for a, b in edges:
            if not union(a, b):
                return False
        return True
```

<a id="lc-0323"></a>
#### 323. Number of Connected Components In An Undirected Graph (Medium)
LeetCode: https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/

- Idea: Union-Find; each successful union reduces the component count by 1.
- Time: `O(n + e * α(n))`
- Space: `O(n)`

```python
class Solution:
    def countComponents(self, n, edges):
        parent = list(range(n))
        rank = [0] * n
        components = n

        def find(x):
            while x != parent[x]:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            nonlocal components
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            components -= 1
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1

        for a, b in edges:
            union(a, b)

        return components
```

<a id="lc-0417"></a>
#### 417. Pacific Atlantic Water Flow (Medium)
LeetCode: https://leetcode.com/problems/pacific-atlantic-water-flow/

- Idea: Reverse the flow: start DFS/BFS from ocean borders and move to equal/higher heights. Intersection are cells reaching both oceans.
- Time: `O(R*C)`
- Space: `O(R*C)`

```python
class Solution:
    def pacificAtlantic(self, heights):
        if not heights or not heights[0]:
            return []

        rows, cols = len(heights), len(heights[0])
        pac = set()
        atl = set()

        def dfs(r, c, seen):
            seen.add((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                    if heights[nr][nc] >= heights[r][c]:
                        dfs(nr, nc, seen)

        for c in range(cols):
            dfs(0, c, pac)
            dfs(rows - 1, c, atl)
        for r in range(rows):
            dfs(r, 0, pac)
            dfs(r, cols - 1, atl)

        return [[r, c] for (r, c) in (pac & atl)]
```

### Advanced Graphs

<a id="lc-0269"></a>
#### 269. Alien Dictionary (Hard)
LeetCode: https://leetcode.com/problems/alien-dictionary/

- Idea: Build a directed graph from first differing character between adjacent words, then topologically sort.
- Edge case: If `w1` is longer and `w1.startswith(w2)`, input is invalid (no ordering).
- Time: `O(total_chars + V + E)`
- Space: `O(V + E)`

```python
from collections import defaultdict, deque


class Solution:
    def alienOrder(self, words):
        graph = defaultdict(set)
        indeg = {ch: 0 for w in words for ch in w}

        for w1, w2 in zip(words, words[1:]):
            if len(w1) > len(w2) and w1.startswith(w2):
                return ""

            for c1, c2 in zip(w1, w2):
                if c1 != c2:
                    if c2 not in graph[c1]:
                        graph[c1].add(c2)
                        indeg[c2] += 1
                    break

        q = deque([ch for ch, d in indeg.items() if d == 0])
        order = []

        while q:
            ch = q.popleft()
            order.append(ch)
            for nei in graph[ch]:
                indeg[nei] -= 1
                if indeg[nei] == 0:
                    q.append(nei)

        return "" if len(order) != len(indeg) else "".join(order)
```

### 1-D Dynamic Programming

<a id="lc-0070"></a>
#### 70. Climbing Stairs (Easy)
LeetCode: https://leetcode.com/problems/climbing-stairs/

- Idea: Fibonacci: `ways[i] = ways[i-1] + ways[i-2]`.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def climbStairs(self, n):
        if n <= 2:
            return n

        a, b = 1, 2
        for _ in range(3, n + 1):
            a, b = b, a + b
        return b
```

<a id="lc-0005"></a>
#### 5. Longest Palindromic Substring (Medium)
LeetCode: https://leetcode.com/problems/longest-palindromic-substring/

- Idea: Expand around each center (odd and even) and keep the best window.
- Time: `O(n^2)`
- Space: `O(1)`

```python
class Solution:
    def longestPalindrome(self, s):
        if not s:
            return ""

        best_l, best_r = 0, 0  # inclusive

        def expand(l, r):
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            return l + 1, r - 1

        for i in range(len(s)):
            l1, r1 = expand(i, i)
            if r1 - l1 > best_r - best_l:
                best_l, best_r = l1, r1
            l2, r2 = expand(i, i + 1)
            if r2 - l2 > best_r - best_l:
                best_l, best_r = l2, r2

        return s[best_l : best_r + 1]
```

<a id="lc-0091"></a>
#### 91. Decode Ways (Medium)
LeetCode: https://leetcode.com/problems/decode-ways/

- Idea: DP over prefix length. A digit can stand alone (1..9) and/or pair with previous (10..26).
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def numDecodings(self, s):
        if not s or s[0] == "0":
            return 0

        dp0, dp1 = 1, 1  # dp[i-2], dp[i-1]
        for i in range(2, len(s) + 1):
            cur = 0
            if s[i - 1] != "0":
                cur += dp1
            two = int(s[i - 2 : i])
            if 10 <= two <= 26:
                cur += dp0
            dp0, dp1 = dp1, cur

        return dp1
```

<a id="lc-0139"></a>
#### 139. Word Break (Medium)
LeetCode: https://leetcode.com/problems/word-break/

##### Approach 1: Bottom-up DP
- Idea: `dp[i]` is True if `s[:i]` can be segmented; try all previous cuts `j < i`.
- Time: `O(n^2)` checks (substring lookup is average `O(1)` with a set)
- Space: `O(n)`

```python
class Solution:
    def wordBreak(self, s, wordDict):
        wordSet = set(wordDict)
        dp = [False] * (len(s) + 1)
        dp[0] = True

        for i in range(1, len(s) + 1):
            for j in range(i):
                if dp[j] and s[j:i] in wordSet:
                    dp[i] = True
                    break

        return dp[-1]
```

##### Approach 2: DFS + memo
- Idea: From index `i`, try matching dictionary words; memoize failed/successful indices.
- Time: Output/input dependent; usually fast with memo and max word length pruning
- Space: `O(n)` memo + recursion

```python
class Solution:
    def wordBreak(self, s, wordDict):
        wordSet = set(wordDict)
        maxLen = max((len(w) for w in wordSet), default=0)
        memo = {}

        def dfs(i):
            if i == len(s):
                return True
            if i in memo:
                return memo[i]

            for j in range(i + 1, min(len(s), i + maxLen) + 1):
                if s[i:j] in wordSet and dfs(j):
                    memo[i] = True
                    return True
            memo[i] = False
            return False

        return dfs(0)
```

<a id="lc-0152"></a>
#### 152. Maximum Product Subarray (Medium)
LeetCode: https://leetcode.com/problems/maximum-product-subarray/

- Idea: Track both max and min products ending at current index (negative flips max/min).
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def maxProduct(self, nums):
        cur_max = cur_min = ans = nums[0]

        for x in nums[1:]:
            if x < 0:
                cur_max, cur_min = cur_min, cur_max
            cur_max = max(x, cur_max * x)
            cur_min = min(x, cur_min * x)
            ans = max(ans, cur_max)

        return ans
```

<a id="lc-0198"></a>
#### 198. House Robber (Medium)
LeetCode: https://leetcode.com/problems/house-robber/

- Idea: DP with two states: `prev1` best up to i-1, `prev2` best up to i-2.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def rob(self, nums):
        prev2 = 0
        prev1 = 0

        for x in nums:
            prev2, prev1 = prev1, max(prev1, prev2 + x)

        return prev1
```

<a id="lc-0213"></a>
#### 213. House Robber II (Medium)
LeetCode: https://leetcode.com/problems/house-robber-ii/

- Idea: Circle constraint means you can't take both first and last. Solve two linear cases and take max.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def rob(self, nums):
        if len(nums) == 1:
            return nums[0]

        def rob_line(arr):
            prev2 = prev1 = 0
            for x in arr:
                prev2, prev1 = prev1, max(prev1, prev2 + x)
            return prev1

        return max(rob_line(nums[:-1]), rob_line(nums[1:]))
```

<a id="lc-0300"></a>
#### 300. Longest Increasing Subsequence (Medium)
LeetCode: https://leetcode.com/problems/longest-increasing-subsequence/

##### Approach 1: `O(n^2)` DP
- Idea: `dp[i]` = LIS ending at i; transition from all `j<i` with `nums[j] < nums[i]`.
- Time: `O(n^2)`
- Space: `O(n)`

```python
class Solution:
    def lengthOfLIS(self, nums):
        n = len(nums)
        dp = [1] * n

        for i in range(n):
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)

        return max(dp, default=0)
```

##### Approach 2: `O(n log n)` patience sorting
- Idea: Maintain `tails[len] = smallest possible tail value of an increasing subsequence of length len+1`.
- Time: `O(n log n)`
- Space: `O(n)`

```python
import bisect


class Solution:
    def lengthOfLIS(self, nums):
        tails = []
        for x in nums:
            i = bisect.bisect_left(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
        return len(tails)
```

<a id="lc-0322"></a>
#### 322. Coin Change (Medium)
LeetCode: https://leetcode.com/problems/coin-change/

##### Approach 1: Bottom-up DP
- Idea: `dp[a]` = min coins to make amount `a`; try each coin.
- Time: `O(amount * numCoins)`
- Space: `O(amount)`

```python
class Solution:
    def coinChange(self, coins, amount):
        INF = amount + 1
        dp = [INF] * (amount + 1)
        dp[0] = 0

        for a in range(1, amount + 1):
            for c in coins:
                if a - c >= 0:
                    dp[a] = min(dp[a], dp[a - c] + 1)

        return -1 if dp[amount] == INF else dp[amount]
```

##### Approach 2: Top-down DFS + memo
- Idea: Try subtracting each coin and memoize the best result for each remaining amount.
- Time: `O(amount * numCoins)` states/transitions
- Space: `O(amount)` memo + recursion

```python
from functools import lru_cache


class Solution:
    def coinChange(self, coins, amount):
        coins = tuple(coins)

        @lru_cache(None)
        def dfs(rem):
            if rem == 0:
                return 0
            if rem < 0:
                return float("inf")
            best = float("inf")
            for c in coins:
                best = min(best, dfs(rem - c) + 1)
            return best

        ans = dfs(amount)
        return -1 if ans == float("inf") else ans
```

<a id="lc-0647"></a>
#### 647. Palindromic Substrings (Medium)
LeetCode: https://leetcode.com/problems/palindromic-substrings/

- Idea: Expand around each center (odd and even) and count.
- Time: `O(n^2)`
- Space: `O(1)`

```python
class Solution:
    def countSubstrings(self, s):
        n = len(s)
        ans = 0

        def expand(l, r):
            nonlocal ans
            while l >= 0 and r < n and s[l] == s[r]:
                ans += 1
                l -= 1
                r += 1

        for i in range(n):
            expand(i, i)
            expand(i, i + 1)

        return ans
```

### 2-D Dynamic Programming

<a id="lc-0062"></a>
#### 62. Unique Paths (Medium)
LeetCode: https://leetcode.com/problems/unique-paths/

- Idea: `dp[r][c] = dp[r-1][c] + dp[r][c-1]`; use 1D DP since each row depends only on previous.
- Time: `O(m*n)`
- Space: `O(n)`

```python
class Solution:
    def uniquePaths(self, m, n):
        dp = [1] * n

        for _ in range(1, m):
            for j in range(1, n):
                dp[j] += dp[j - 1]

        return dp[-1]
```

<a id="lc-1143"></a>
#### 1143. Longest Common Subsequence (Medium)
LeetCode: https://leetcode.com/problems/longest-common-subsequence/

- Idea: 2D DP: `dp[i][j]` = LCS length for suffixes `text1[i:]`, `text2[j:]`.
- Time: `O(m*n)`
- Space: `O(m*n)`

```python
class Solution:
    def longestCommonSubsequence(self, text1, text2):
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if text1[i] == text2[j]:
                    dp[i][j] = 1 + dp[i + 1][j + 1]
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])

        return dp[0][0]
```

### Greedy

<a id="lc-0053"></a>
#### 53. Maximum Subarray (Medium)
LeetCode: https://leetcode.com/problems/maximum-subarray/

- Idea: Kadane's algorithm: best subarray ending at `i` is either `nums[i]` or extend previous.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def maxSubArray(self, nums):
        best = cur = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best
```

<a id="lc-0055"></a>
#### 55. Jump Game (Medium)
LeetCode: https://leetcode.com/problems/jump-game/

- Idea: Greedy keep the farthest reachable index; fail if you land beyond it.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def canJump(self, nums):
        farthest = 0
        for i, jump in enumerate(nums):
            if i > farthest:
                return False
            farthest = max(farthest, i + jump)
        return True
```

### Intervals

<a id="lc-0252"></a>
#### 252. Meeting Rooms (Easy)
LeetCode: https://leetcode.com/problems/meeting-rooms/

- Idea: Sort by start time; any overlap means you can't attend all meetings.
- Time: `O(n log n)`
- Space: `O(1)` extra (sorting aside)

```python
class Solution:
    def canAttendMeetings(self, intervals):
        intervals.sort(key=lambda x: x[0])
        for i in range(1, len(intervals)):
            if intervals[i][0] < intervals[i - 1][1]:
                return False
        return True
```

<a id="lc-0056"></a>
#### 56. Merge Intervals (Medium)
LeetCode: https://leetcode.com/problems/merge-intervals/

- Idea: Sort by start; extend the current merged interval while overlaps continue.
- Time: `O(n log n)`
- Space: `O(n)` for output

```python
class Solution:
    def merge(self, intervals):
        intervals.sort(key=lambda x: x[0])
        merged = []

        for start, end in intervals:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        return merged
```

<a id="lc-0057"></a>
#### 57. Insert Interval (Medium)
LeetCode: https://leetcode.com/problems/insert-interval/

- Idea: Add all intervals before `newInterval`, merge overlaps with it, then append the rest.
- Time: `O(n)`
- Space: `O(n)` for output

```python
class Solution:
    def insert(self, intervals, newInterval):
        res = []
        i = 0
        n = len(intervals)
        start, end = newInterval

        while i < n and intervals[i][1] < start:
            res.append(intervals[i])
            i += 1

        while i < n and intervals[i][0] <= end:
            start = min(start, intervals[i][0])
            end = max(end, intervals[i][1])
            i += 1
        res.append([start, end])

        while i < n:
            res.append(intervals[i])
            i += 1

        return res
```

<a id="lc-0253"></a>
#### 253. Meeting Rooms II (Medium)
LeetCode: https://leetcode.com/problems/meeting-rooms-ii/

##### Approach 1: Min-heap of end times
- Idea: Reuse a room if the earliest-ending meeting ends before the next starts; otherwise allocate a new room.
- Time: `O(n log n)`
- Space: `O(n)` heap worst-case

```python
import heapq


class Solution:
    def minMeetingRooms(self, intervals):
        if not intervals:
            return 0

        intervals.sort(key=lambda x: x[0])
        heap = []

        for start, end in intervals:
            if heap and heap[0] <= start:
                heapq.heapreplace(heap, end)
            else:
                heapq.heappush(heap, end)

        return len(heap)
```

##### Approach 2: Sweep line
- Idea: Convert each interval into `(start, +1)` and `(end, -1)` events; max prefix sum is the answer.
- Time: `O(n log n)`
- Space: `O(n)`

```python
class Solution:
    def minMeetingRooms(self, intervals):
        events = []
        for s, e in intervals:
            events.append((s, 1))
            events.append((e, -1))

        # process endings before starts at the same time
        events.sort(key=lambda x: (x[0], x[1]))

        rooms = best = 0
        for _, delta in events:
            rooms += delta
            best = max(best, rooms)
        return best
```

<a id="lc-0435"></a>
#### 435. Non Overlapping Intervals (Medium)
LeetCode: https://leetcode.com/problems/non-overlapping-intervals/

- Idea: Greedy sort by end time; keep the interval with the earliest end to leave room for future intervals.
- Time: `O(n log n)`
- Space: `O(1)` extra

```python
class Solution:
    def eraseOverlapIntervals(self, intervals):
        if not intervals:
            return 0

        intervals.sort(key=lambda x: x[1])
        end = intervals[0][1]
        removed = 0

        for s, e in intervals[1:]:
            if s < end:
                removed += 1
            else:
                end = e

        return removed
```

### Math & Geometry

<a id="lc-0048"></a>
#### 48. Rotate Image (Medium)
LeetCode: https://leetcode.com/problems/rotate-image/

- Idea: Rotate 90° clockwise = transpose + reverse each row.
- Time: `O(n^2)`
- Space: `O(1)`

```python
class Solution:
    def rotate(self, matrix):
        n = len(matrix)

        # transpose
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

        # reverse each row
        for row in matrix:
            row.reverse()
```

<a id="lc-0054"></a>
#### 54. Spiral Matrix (Medium)
LeetCode: https://leetcode.com/problems/spiral-matrix/

- Idea: Maintain boundaries (top, bottom, left, right) and peel layers.
- Time: `O(R*C)`
- Space: `O(1)` extra (output aside)

```python
class Solution:
    def spiralOrder(self, matrix):
        res = []
        if not matrix or not matrix[0]:
            return res

        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1

        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                res.append(matrix[top][c])
            top += 1

            for r in range(top, bottom + 1):
                res.append(matrix[r][right])
            right -= 1

            if top <= bottom:
                for c in range(right, left - 1, -1):
                    res.append(matrix[bottom][c])
                bottom -= 1

            if left <= right:
                for r in range(bottom, top - 1, -1):
                    res.append(matrix[r][left])
                left += 1

        return res
```

<a id="lc-0073"></a>
#### 73. Set Matrix Zeroes (Medium)
LeetCode: https://leetcode.com/problems/set-matrix-zeroes/

##### Approach 1: Row/column sets
- Idea: First pass records which rows/cols must be zeroed; second pass writes zeros.
- Time: `O(R*C)`
- Space: `O(R + C)`

```python
class Solution:
    def setZeroes(self, matrix):
        rows = set()
        cols = set()
        R, C = len(matrix), len(matrix[0])

        for r in range(R):
            for c in range(C):
                if matrix[r][c] == 0:
                    rows.add(r)
                    cols.add(c)

        for r in range(R):
            for c in range(C):
                if r in rows or c in cols:
                    matrix[r][c] = 0
```

##### Approach 2: In-place markers (`O(1)` extra space)
- Idea: Use first row/col as marker arrays; handle whether they originally contain zeros.
- Time: `O(R*C)`
- Space: `O(1)`

```python
class Solution:
    def setZeroes(self, matrix):
        R, C = len(matrix), len(matrix[0])
        first_row_zero = any(matrix[0][c] == 0 for c in range(C))
        first_col_zero = any(matrix[r][0] == 0 for r in range(R))

        for r in range(1, R):
            for c in range(1, C):
                if matrix[r][c] == 0:
                    matrix[r][0] = 0
                    matrix[0][c] = 0

        for r in range(1, R):
            for c in range(1, C):
                if matrix[r][0] == 0 or matrix[0][c] == 0:
                    matrix[r][c] = 0

        if first_row_zero:
            for c in range(C):
                matrix[0][c] = 0
        if first_col_zero:
            for r in range(R):
                matrix[r][0] = 0
```

### Bit Manipulation

<a id="lc-0190"></a>
#### 190. Reverse Bits (Easy)
LeetCode: https://leetcode.com/problems/reverse-bits/

- Idea: Build the reversed number by shifting result left and reading bits from `n`.
- Time: `O(1)` (32 iterations)
- Space: `O(1)`

```python
class Solution:
    def reverseBits(self, n):
        res = 0
        for _ in range(32):
            res = (res << 1) | (n & 1)
            n >>= 1
        return res
```

<a id="lc-0191"></a>
#### 191. Number of 1 Bits (Easy)
LeetCode: https://leetcode.com/problems/number-of-1-bits/

- Idea: Repeatedly clear the lowest set bit with `n &= n-1`.
- Time: `O(popcount(n))`
- Space: `O(1)`

```python
class Solution:
    def hammingWeight(self, n):
        count = 0
        while n:
            n &= n - 1
            count += 1
        return count
```

<a id="lc-0268"></a>
#### 268. Missing Number (Easy)
LeetCode: https://leetcode.com/problems/missing-number/

- Idea: XOR all indices and values together; pairs cancel leaving the missing number.
- Time: `O(n)`
- Space: `O(1)`

```python
class Solution:
    def missingNumber(self, nums):
        res = len(nums)
        for i, x in enumerate(nums):
            res ^= i ^ x
        return res
```

<a id="lc-0338"></a>
#### 338. Counting Bits (Easy)
LeetCode: https://leetcode.com/problems/counting-bits/

- Idea: `bits[i] = bits[i >> 1] + (i & 1)`.
- Time: `O(n)`
- Space: `O(n)`

```python
class Solution:
    def countBits(self, n):
        ans = [0] * (n + 1)
        for i in range(1, n + 1):
            ans[i] = ans[i >> 1] + (i & 1)
        return ans
```

<a id="lc-0371"></a>
#### 371. Sum of Two Integers (Medium)
LeetCode: https://leetcode.com/problems/sum-of-two-integers/

- Idea: Bitwise addition: `xor` gives sum without carry; `(a&b)<<1` gives carry. Repeat until carry is 0.
- Note: Python ints are unbounded, so mask to 32-bit to emulate signed int behavior.
- Time: `O(1)` (bounded by word size)
- Space: `O(1)`

```python
class Solution:
    def getSum(self, a, b):
        mask = 0xFFFFFFFF

        while b & mask:
            carry = (a & b) << 1
            a = (a ^ b) & mask
            b = carry & mask

        return a if a <= 0x7FFFFFFF else ~(a ^ mask)
```
