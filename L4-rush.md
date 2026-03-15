# Google L4 DSA Interview Prep Plans

> **Language:** Python  
> **Target:** Google L4 (SWE III) — OA + Phone Screen + Onsite  
> **Source:** NeetCode 150 + Google-tagged LeetCode problems  
> **Difficulty key:** 🟢 Easy · 🟡 Medium · 🔴 Hard

---

## Quick Reference — Difficulty Distribution by Plan

| Plan | Total | Easy | Medium | Hard | Daily avg |
|---|---|---|---|---|---|
| [1-week / 50q](#plan-1) | 50 | 8 | 30 | 12 | 7/day |
| [1-week / 100q](#plan-2) | 100 | 12 | 60 | 28 | 14/day |
| [1-week / 150q](#plan-3) | 150 | 18 | 90 | 42 | 21/day |
| [2-week / 90q](#plan-4) | 90 | 12 | 55 | 23 | 6–7/day |
| [2-week / 150q](#plan-5) | 150 | 18 | 90 | 42 | 10–11/day |
| [4-week / 150q](#plan-6) | 150 | 18 | 90 | 42 | 5/day |

---

## Topic Priority for Google L4

Ordered by real interview frequency based on L4 candidate reports:

1. **Graphs** (BFS/DFS/Topo) — highest frequency, every onsite
2. **Dynamic Programming** — appears in 2 of 3 onsite rounds
3. **Trees** (DFS/BFS) — always tested
4. **Heap / Priority Queue** — Top-K is a Google favourite
5. **Arrays + Hashmaps** — OA and phone screen staple
6. **Binary Search** — disguised in many problems
7. **Sliding Window** — OA staple
8. **Backtracking** — appears occasionally
9. **Stack / Monotonic Stack** — supporting pattern
10. **Trie** — lower frequency, but Google-specific (autocomplete)
11. **Linked List** — mostly phone screen warm-up
12. **Intervals** — scheduling problems
13. **Bit Manipulation** — rare, easy points

---

## Python Essentials — Drill Daily (10 min)

```python
# Min-heap
import heapq
heapq.heappush(h, val)
heapq.heappop(h)
heapq.heappush(h, -val)        # max-heap trick

# BFS
from collections import deque
q = deque([start])
visited = {start}
while q:
    node = q.popleft()

# Graph
from collections import defaultdict
graph = defaultdict(list)

# Frequency
from collections import Counter
Counter(nums).most_common(k)
```

---

---

<a id="plan-1"></a>
# PLAN 1 — 1 Week / 50 Questions

> **Intensity:** 7 problems/day · 4–5 hrs/day  
> **Coverage:** OA + phone screen minimum bar  
> **Strategy:** One topic per day, highest-frequency topics only

---

### Day 1 — Arrays + Hashmaps (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Two Sum | 🟢 Easy | #1 |
| 2 | Contains Duplicate | 🟢 Easy | #217 |
| 3 | Product of Array Except Self | 🟡 Medium | #238 |
| 4 | Top K Frequent Elements | 🟡 Medium | #347 |
| 5 | Group Anagrams | 🟡 Medium | #49 |
| 6 | Longest Consecutive Sequence | 🟡 Medium | #128 |
| 7 | Valid Anagram | 🟢 Easy | #242 |

> **Focus:** HashMap as default tool. Every array problem — think map first.

---

### Day 2 — Graphs: BFS/DFS (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Number of Islands | 🟡 Medium | #200 |
| 2 | Clone Graph | 🟡 Medium | #133 |
| 3 | Rotting Oranges | 🟡 Medium | #994 |
| 4 | Pacific Atlantic Water Flow | 🟡 Medium | #417 |
| 5 | Course Schedule | 🟡 Medium | #207 |
| 6 | Course Schedule II | 🟡 Medium | #210 |
| 7 | Word Ladder | 🔴 Hard | #127 |

> **Focus:** Implement BFS and DFS from scratch for grid and adjacency list. Add a `visited` set — that's the only difference from tree DFS.

---

### Day 3 — Trees (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Invert Binary Tree | 🟢 Easy | #226 |
| 2 | Max Depth of Binary Tree | 🟢 Easy | #104 |
| 3 | Binary Tree Level Order Traversal | 🟡 Medium | #102 |
| 4 | Validate BST | 🟡 Medium | #98 |
| 5 | Lowest Common Ancestor | 🟡 Medium | #236 |
| 6 | Binary Tree Max Path Sum | 🔴 Hard | #124 |
| 7 | Serialize / Deserialize Binary Tree | 🔴 Hard | #297 |

> **Focus:** Recursive DFS with a return value. Write it cold in 5 min — this is table stakes.

---

### Day 4 — Heap + Sliding Window (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Kth Largest Element in Array | 🟡 Medium | #215 |
| 2 | K Closest Points to Origin | 🟡 Medium | #973 |
| 3 | Find Median from Data Stream | 🔴 Hard | #295 |
| 4 | Merge K Sorted Lists | 🔴 Hard | #23 |
| 5 | Best Time to Buy/Sell Stock | 🟢 Easy | #121 |
| 6 | Longest Substring Without Repeating | 🟡 Medium | #3 |
| 7 | Minimum Window Substring | 🔴 Hard | #76 |

> **Focus:** Min-heap of size K for Top-K largest. Variable sliding window: expand right, shrink left when invalid.

---

### Day 5 — Dynamic Programming (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Climbing Stairs | 🟢 Easy | #70 |
| 2 | House Robber | 🟡 Medium | #198 |
| 3 | Coin Change | 🟡 Medium | #322 |
| 4 | Word Break | 🟡 Medium | #139 |
| 5 | Decode Ways | 🟡 Medium | #91 |
| 6 | Longest Increasing Subsequence | 🟡 Medium | #300 |
| 7 | Edit Distance | 🔴 Hard | #72 |

> **Focus:** DP state = "what do I need to know at position i to decide optimally?" Define state before coding.

---

### Day 6 — Binary Search + Intervals (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Search in Rotated Sorted Array | 🟡 Medium | #33 |
| 2 | Find Minimum in Rotated Array | 🟡 Medium | #153 |
| 3 | Koko Eating Bananas | 🟡 Medium | #875 |
| 4 | Median of Two Sorted Arrays | 🔴 Hard | #4 |
| 5 | Merge Intervals | 🟡 Medium | #56 |
| 6 | Non-overlapping Intervals | 🟡 Medium | #435 |
| 7 | Meeting Rooms II | 🟡 Medium | #253 |

> **Focus:** "Minimum/maximum satisfying a condition" → binary search on the answer space immediately.

---

### Day 7 — Mock Day (6 problems, 30 min each, no hints)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | LRU Cache | 🟡 Medium | #146 |
| 2 | Jump Game II | 🟡 Medium | #45 |
| 3 | Number of Connected Components | 🟡 Medium | #323 |
| 4 | Redundant Connection | 🟡 Medium | #684 |
| 5 | Alien Dictionary | 🔴 Hard | #269 |
| 6 | Burst Balloons | 🔴 Hard | #312 |

> **Rules:** Timer on. Write in plain text editor (no IDE). Say every thought out loud. After each problem: state time/space complexity before checking answer.

---

---

<a id="plan-2"></a>
# PLAN 2 — 1 Week / 100 Questions

> **Intensity:** 14 problems/day · 7–8 hrs/day  
> **Coverage:** All rounds — OA + phone screen + onsite  
> **Strategy:** Two topics per day, full NeetCode 150 core

---

### Day 1 — Arrays + Hashmaps + Two Pointers (14 problems)

**Arrays + Hashmaps (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Two Sum | 🟢 Easy | #1 |
| 2 | Contains Duplicate | 🟢 Easy | #217 |
| 3 | Valid Anagram | 🟢 Easy | #242 |
| 4 | Group Anagrams | 🟡 Medium | #49 |
| 5 | Top K Frequent Elements | 🟡 Medium | #347 |
| 6 | Product of Array Except Self | 🟡 Medium | #238 |
| 7 | Longest Consecutive Sequence | 🟡 Medium | #128 |

**Two Pointers (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Valid Palindrome | 🟢 Easy | #125 |
| 9 | Two Sum II (sorted) | 🟡 Medium | #167 |
| 10 | 3Sum | 🟡 Medium | #15 |
| 11 | Container With Most Water | 🟡 Medium | #11 |
| 12 | Trapping Rain Water | 🔴 Hard | #42 |
| 13 | Move Zeroes | 🟢 Easy | #283 |
| 14 | Remove Duplicates from Sorted Array | 🟢 Easy | #26 |

---

### Day 2 — Sliding Window + Stack (14 problems)

**Sliding Window (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Best Time to Buy/Sell Stock | 🟢 Easy | #121 |
| 2 | Longest Substring Without Repeating | 🟡 Medium | #3 |
| 3 | Longest Repeating Char Replacement | 🟡 Medium | #424 |
| 4 | Permutation in String | 🟡 Medium | #567 |
| 5 | Minimum Window Substring | 🔴 Hard | #76 |
| 6 | Sliding Window Maximum | 🔴 Hard | #239 |

**Stack (8)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 7 | Valid Parentheses | 🟢 Easy | #20 |
| 8 | Min Stack | 🟡 Medium | #155 |
| 9 | Daily Temperatures | 🟡 Medium | #739 |
| 10 | Car Fleet | 🟡 Medium | #853 |
| 11 | Largest Rectangle in Histogram | 🔴 Hard | #84 |
| 12 | Evaluate Reverse Polish Notation | 🟡 Medium | #150 |
| 13 | Generate Parentheses | 🟡 Medium | #22 |
| 14 | Decode String | 🟡 Medium | #394 |

---

### Day 3 — Binary Search + Linked List (14 problems)

**Binary Search (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Binary Search | 🟢 Easy | #704 |
| 2 | Search in Rotated Sorted Array | 🟡 Medium | #33 |
| 3 | Find Minimum in Rotated Array | 🟡 Medium | #153 |
| 4 | Koko Eating Bananas | 🟡 Medium | #875 |
| 5 | Search a 2D Matrix | 🟡 Medium | #74 |
| 6 | Time Based Key-Value Store | 🟡 Medium | #981 |
| 7 | Median of Two Sorted Arrays | 🔴 Hard | #4 |

**Linked List (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Reverse Linked List | 🟢 Easy | #206 |
| 9 | Merge Two Sorted Lists | 🟢 Easy | #21 |
| 10 | Linked List Cycle | 🟢 Easy | #141 |
| 11 | Reorder List | 🟡 Medium | #143 |
| 12 | Remove Nth Node From End | 🟡 Medium | #19 |
| 13 | Copy List with Random Pointer | 🟡 Medium | #138 |
| 14 | LRU Cache | 🟡 Medium | #146 |

---

### Day 4 — Trees (14 problems)

**Trees — DFS (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Invert Binary Tree | 🟢 Easy | #226 |
| 2 | Max Depth of Binary Tree | 🟢 Easy | #104 |
| 3 | Diameter of Binary Tree | 🟢 Easy | #543 |
| 4 | Validate BST | 🟡 Medium | #98 |
| 5 | Construct Tree from Pre+Inorder | 🟡 Medium | #105 |
| 6 | Kth Smallest in BST | 🟡 Medium | #230 |
| 7 | Lowest Common Ancestor | 🟡 Medium | #236 |

**Trees — BFS + Advanced (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Binary Tree Level Order Traversal | 🟡 Medium | #102 |
| 9 | Binary Tree Right Side View | 🟡 Medium | #199 |
| 10 | Count Good Nodes in Tree | 🟡 Medium | #1448 |
| 11 | Binary Tree Zigzag Level Order | 🟡 Medium | #103 |
| 12 | Path Sum III | 🟡 Medium | #437 |
| 13 | Binary Tree Max Path Sum | 🔴 Hard | #124 |
| 14 | Serialize / Deserialize Binary Tree | 🔴 Hard | #297 |

---

### Day 5 — Graphs (14 problems)

**Graphs — BFS/DFS (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Number of Islands | 🟡 Medium | #200 |
| 2 | Clone Graph | 🟡 Medium | #133 |
| 3 | Rotting Oranges | 🟡 Medium | #994 |
| 4 | Pacific Atlantic Water Flow | 🟡 Medium | #417 |
| 5 | Surrounded Regions | 🟡 Medium | #130 |
| 6 | Walls and Gates | 🟡 Medium | #286 |
| 7 | Word Ladder | 🔴 Hard | #127 |

**Graphs — Topo Sort + Union Find (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Course Schedule | 🟡 Medium | #207 |
| 9 | Course Schedule II | 🟡 Medium | #210 |
| 10 | Number of Connected Components | 🟡 Medium | #323 |
| 11 | Redundant Connection | 🟡 Medium | #684 |
| 12 | Graph Valid Tree | 🟡 Medium | #261 |
| 13 | Accounts Merge | 🟡 Medium | #721 |
| 14 | Alien Dictionary | 🔴 Hard | #269 |

---

### Day 6 — Heap + Dynamic Programming (14 problems)

**Heap (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Kth Largest Element in Array | 🟡 Medium | #215 |
| 2 | K Closest Points to Origin | 🟡 Medium | #973 |
| 3 | Task Scheduler | 🟡 Medium | #621 |
| 4 | Design Twitter (heap) | 🟡 Medium | #355 |
| 5 | Find Median from Data Stream | 🔴 Hard | #295 |
| 6 | Merge K Sorted Lists | 🔴 Hard | #23 |

**DP — 1D (8)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 7 | Climbing Stairs | 🟢 Easy | #70 |
| 8 | House Robber | 🟡 Medium | #198 |
| 9 | House Robber II | 🟡 Medium | #213 |
| 10 | Coin Change | 🟡 Medium | #322 |
| 11 | Word Break | 🟡 Medium | #139 |
| 12 | Decode Ways | 🟡 Medium | #91 |
| 13 | Longest Increasing Subsequence | 🟡 Medium | #300 |
| 14 | Coin Change II | 🟡 Medium | #518 |

---

### Day 7 — DP 2D + Backtracking + Mock (14 problems)

**DP — 2D (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Unique Paths | 🟡 Medium | #62 |
| 2 | Longest Common Subsequence | 🟡 Medium | #1143 |
| 3 | Edit Distance | 🔴 Hard | #72 |
| 4 | Maximal Square | 🟡 Medium | #221 |
| 5 | Burst Balloons | 🔴 Hard | #312 |

**Backtracking (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 6 | Subsets | 🟡 Medium | #78 |
| 7 | Combination Sum | 🟡 Medium | #39 |
| 8 | Permutations | 🟡 Medium | #46 |
| 9 | Word Search | 🟡 Medium | #79 |
| 10 | N-Queens | 🔴 Hard | #51 |

**Mock — timed 30 min each (4)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 11 | Jump Game II | 🟡 Medium | #45 |
| 12 | Maximum Profit in Job Scheduling | 🔴 Hard | #1235 |
| 13 | Implement Trie | 🟡 Medium | #208 |
| 14 | Word Search II | 🔴 Hard | #212 |

---

---

<a id="plan-3"></a>
# PLAN 3 — 1 Week / 150 Questions

> **Intensity:** 21 problems/day · 10–12 hrs/day  
> **Coverage:** Full NeetCode 150 — complete preparation  
> **Note:** Extreme. Only attempt if you have full days free with no other obligations.

---

### Day 1 — Arrays + Two Pointers + Sliding Window + Stack (21 problems)

**Arrays + Hashmaps (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Two Sum | 🟢 Easy | #1 |
| 2 | Contains Duplicate | 🟢 Easy | #217 |
| 3 | Valid Anagram | 🟢 Easy | #242 |
| 4 | Group Anagrams | 🟡 Medium | #49 |
| 5 | Top K Frequent Elements | 🟡 Medium | #347 |
| 6 | Product of Array Except Self | 🟡 Medium | #238 |
| 7 | Longest Consecutive Sequence | 🟡 Medium | #128 |

**Two Pointers (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Valid Palindrome | 🟢 Easy | #125 |
| 9 | 3Sum | 🟡 Medium | #15 |
| 10 | Container With Most Water | 🟡 Medium | #11 |
| 11 | Trapping Rain Water | 🔴 Hard | #42 |
| 12 | Two Sum II | 🟡 Medium | #167 |

**Sliding Window (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 13 | Best Time to Buy/Sell Stock | 🟢 Easy | #121 |
| 14 | Longest Substring Without Repeating | 🟡 Medium | #3 |
| 15 | Longest Repeating Char Replacement | 🟡 Medium | #424 |
| 16 | Minimum Window Substring | 🔴 Hard | #76 |
| 17 | Sliding Window Maximum | 🔴 Hard | #239 |

**Stack (4)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 18 | Valid Parentheses | 🟢 Easy | #20 |
| 19 | Min Stack | 🟡 Medium | #155 |
| 20 | Daily Temperatures | 🟡 Medium | #739 |
| 21 | Largest Rectangle in Histogram | 🔴 Hard | #84 |

---

### Day 2 — Binary Search + Linked List + Intervals (21 problems)

**Binary Search (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Binary Search | 🟢 Easy | #704 |
| 2 | Search in Rotated Sorted Array | 🟡 Medium | #33 |
| 3 | Find Minimum in Rotated Array | 🟡 Medium | #153 |
| 4 | Koko Eating Bananas | 🟡 Medium | #875 |
| 5 | Search a 2D Matrix | 🟡 Medium | #74 |
| 6 | Time Based Key-Value Store | 🟡 Medium | #981 |
| 7 | Median of Two Sorted Arrays | 🔴 Hard | #4 |

**Linked List (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Reverse Linked List | 🟢 Easy | #206 |
| 9 | Merge Two Sorted Lists | 🟢 Easy | #21 |
| 10 | Linked List Cycle | 🟢 Easy | #141 |
| 11 | Reorder List | 🟡 Medium | #143 |
| 12 | Remove Nth Node From End | 🟡 Medium | #19 |
| 13 | Copy List with Random Pointer | 🟡 Medium | #138 |
| 14 | LRU Cache | 🟡 Medium | #146 |

**Intervals (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 15 | Insert Interval | 🟡 Medium | #57 |
| 16 | Merge Intervals | 🟡 Medium | #56 |
| 17 | Non-overlapping Intervals | 🟡 Medium | #435 |
| 18 | Meeting Rooms | 🟢 Easy | #252 |
| 19 | Meeting Rooms II | 🟡 Medium | #253 |
| 20 | Minimum Interval to Include Each Query | 🔴 Hard | #1851 |
| 21 | Jump Game II | 🟡 Medium | #45 |

---

### Day 3 — Trees (21 problems)

**Trees — Basic DFS (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Invert Binary Tree | 🟢 Easy | #226 |
| 2 | Max Depth of Binary Tree | 🟢 Easy | #104 |
| 3 | Diameter of Binary Tree | 🟢 Easy | #543 |
| 4 | Balanced Binary Tree | 🟢 Easy | #110 |
| 5 | Same Tree | 🟢 Easy | #100 |
| 6 | Subtree of Another Tree | 🟢 Easy | #572 |
| 7 | Symmetric Tree | 🟢 Easy | #101 |

**Trees — BST + Construct (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Validate BST | 🟡 Medium | #98 |
| 9 | Kth Smallest in BST | 🟡 Medium | #230 |
| 10 | Lowest Common Ancestor BST | 🟡 Medium | #235 |
| 11 | Construct Tree from Pre+Inorder | 🟡 Medium | #105 |
| 12 | Insert into BST | 🟡 Medium | #701 |
| 13 | Delete Node in BST | 🟡 Medium | #450 |
| 14 | Binary Search Tree Iterator | 🟡 Medium | #173 |

**Trees — BFS + Advanced (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 15 | Binary Tree Level Order Traversal | 🟡 Medium | #102 |
| 16 | Binary Tree Right Side View | 🟡 Medium | #199 |
| 17 | Count Good Nodes in Tree | 🟡 Medium | #1448 |
| 18 | Path Sum III | 🟡 Medium | #437 |
| 19 | Lowest Common Ancestor BT | 🟡 Medium | #236 |
| 20 | Binary Tree Max Path Sum | 🔴 Hard | #124 |
| 21 | Serialize / Deserialize Binary Tree | 🔴 Hard | #297 |

---

### Day 4 — Heap + Graphs BFS/DFS (21 problems)

**Heap (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Kth Largest Element in Array | 🟡 Medium | #215 |
| 2 | K Closest Points to Origin | 🟡 Medium | #973 |
| 3 | Top K Frequent Elements (heap) | 🟡 Medium | #347 |
| 4 | Task Scheduler | 🟡 Medium | #621 |
| 5 | Design Twitter (heap) | 🟡 Medium | #355 |
| 6 | Find Median from Data Stream | 🔴 Hard | #295 |
| 7 | Merge K Sorted Lists | 🔴 Hard | #23 |

**Graphs — BFS/DFS (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Number of Islands | 🟡 Medium | #200 |
| 9 | Clone Graph | 🟡 Medium | #133 |
| 10 | Rotting Oranges | 🟡 Medium | #994 |
| 11 | Pacific Atlantic Water Flow | 🟡 Medium | #417 |
| 12 | Surrounded Regions | 🟡 Medium | #130 |
| 13 | Walls and Gates | 🟡 Medium | #286 |
| 14 | Word Ladder | 🔴 Hard | #127 |

**Graphs — Topo Sort + Union Find (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 15 | Course Schedule | 🟡 Medium | #207 |
| 16 | Course Schedule II | 🟡 Medium | #210 |
| 17 | Number of Connected Components | 🟡 Medium | #323 |
| 18 | Redundant Connection | 🟡 Medium | #684 |
| 19 | Accounts Merge | 🟡 Medium | #721 |
| 20 | Alien Dictionary | 🔴 Hard | #269 |
| 21 | Graph Valid Tree | 🟡 Medium | #261 |

---

### Day 5 — Dynamic Programming (21 problems)

**DP — 1D Core (8)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Climbing Stairs | 🟢 Easy | #70 |
| 2 | House Robber | 🟡 Medium | #198 |
| 3 | House Robber II | 🟡 Medium | #213 |
| 4 | Coin Change | 🟡 Medium | #322 |
| 5 | Coin Change II | 🟡 Medium | #518 |
| 6 | Decode Ways | 🟡 Medium | #91 |
| 7 | Word Break | 🟡 Medium | #139 |
| 8 | Longest Increasing Subsequence | 🟡 Medium | #300 |

**DP — Stocks (3)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 9 | Best Time to Buy/Sell Stock | 🟢 Easy | #121 |
| 10 | Best Time to Buy/Sell with Cooldown | 🟡 Medium | #309 |
| 11 | Best Time to Buy/Sell III (max 2 tx) | 🔴 Hard | #123 |

**DP — 2D (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 12 | Unique Paths | 🟡 Medium | #62 |
| 13 | Longest Common Subsequence | 🟡 Medium | #1143 |
| 14 | Edit Distance | 🔴 Hard | #72 |
| 15 | Maximal Square | 🟡 Medium | #221 |
| 16 | Distinct Subsequences | 🔴 Hard | #115 |

**DP — Advanced (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 17 | Partition Equal Subset Sum | 🟡 Medium | #416 |
| 18 | Target Sum | 🟡 Medium | #494 |
| 19 | Burst Balloons | 🔴 Hard | #312 |
| 20 | Regular Expression Matching | 🔴 Hard | #10 |
| 21 | Maximum Profit in Job Scheduling | 🔴 Hard | #1235 |

---

### Day 6 — Backtracking + Trie + Bit Manipulation (21 problems)

**Backtracking (7)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Subsets | 🟡 Medium | #78 |
| 2 | Subsets II (duplicates) | 🟡 Medium | #90 |
| 3 | Combination Sum | 🟡 Medium | #39 |
| 4 | Combination Sum II | 🟡 Medium | #40 |
| 5 | Permutations | 🟡 Medium | #46 |
| 6 | Word Search | 🟡 Medium | #79 |
| 7 | N-Queens | 🔴 Hard | #51 |

**Trie (3)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 8 | Implement Trie | 🟡 Medium | #208 |
| 9 | Design Add and Search Words | 🟡 Medium | #211 |
| 10 | Word Search II | 🔴 Hard | #212 |

**Bit Manipulation (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 11 | Number of 1 Bits | 🟢 Easy | #191 |
| 12 | Counting Bits | 🟢 Easy | #338 |
| 13 | Missing Number | 🟢 Easy | #268 |
| 14 | Reverse Bits | 🟢 Easy | #190 |
| 15 | Sum of Two Integers | 🟡 Medium | #371 |

**Intervals + Misc (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 16 | Gas Station | 🟡 Medium | #134 |
| 17 | Hand of Straights | 🟡 Medium | #846 |
| 18 | Merge Triplets to Form Target | 🟡 Medium | #1899 |
| 19 | Partition Labels | 🟡 Medium | #763 |
| 20 | Minimum Number of Arrows | 🟡 Medium | #452 |
| 21 | Insert Interval | 🟡 Medium | #57 |

---

### Day 7 — Mock Day (full NeetCode 150 gaps + 2 timed sessions)

Solve all remaining NeetCode 150 problems not covered in Days 1–6, then run:
- **Session 1 (morning):** 45 min · 1 medium + 1 hard · plain text editor · no hints
- **Session 2 (afternoon):** 45 min · 1 medium + 1 hard · new problems only

---

---

<a id="plan-4"></a>
# PLAN 4 — 2 Weeks / 90 Questions

> **Intensity:** 6–7 problems/day · 2–3 hrs/day  
> **Coverage:** OA + phone screen + onsite — solid bar  
> **Strategy:** One concentrated topic per day, ordered by Google interview frequency

---

### Day 1 — Graphs: BFS/DFS (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Number of Islands | 🟡 Medium | #200 |
| 2 | Clone Graph | 🟡 Medium | #133 |
| 3 | Rotting Oranges | 🟡 Medium | #994 |
| 4 | Pacific Atlantic Water Flow | 🟡 Medium | #417 |
| 5 | Surrounded Regions | 🟡 Medium | #130 |
| 6 | Word Ladder | 🔴 Hard | #127 |

> **Pattern to lock in:** Multi-source BFS — start from all sources simultaneously. Add `visited` set to every DFS.

---

### Day 2 — Graphs: Topological Sort + Union Find (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Course Schedule | 🟡 Medium | #207 |
| 2 | Course Schedule II | 🟡 Medium | #210 |
| 3 | Number of Connected Components | 🟡 Medium | #323 |
| 4 | Redundant Connection | 🟡 Medium | #684 |
| 5 | Accounts Merge | 🟡 Medium | #721 |
| 6 | Alien Dictionary | 🔴 Hard | #269 |

> **Pattern to lock in:** Kahn's algorithm (BFS topo sort) and Union-Find with path compression. Both from memory.

---

### Day 3 — Trees: DFS (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Invert Binary Tree | 🟢 Easy | #226 |
| 2 | Max Depth of Binary Tree | 🟢 Easy | #104 |
| 3 | Validate BST | 🟡 Medium | #98 |
| 4 | Lowest Common Ancestor | 🟡 Medium | #236 |
| 5 | Binary Tree Max Path Sum | 🔴 Hard | #124 |
| 6 | Serialize / Deserialize Binary Tree | 🔴 Hard | #297 |

---

### Day 4 — Trees: BFS + BST (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Binary Tree Level Order Traversal | 🟡 Medium | #102 |
| 2 | Binary Tree Right Side View | 🟡 Medium | #199 |
| 3 | Count Good Nodes in Tree | 🟡 Medium | #1448 |
| 4 | Kth Smallest in BST | 🟡 Medium | #230 |
| 5 | Construct Tree from Pre+Inorder | 🟡 Medium | #105 |
| 6 | Path Sum III | 🟡 Medium | #437 |

---

### Day 5 — Dynamic Programming: 1D (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Climbing Stairs | 🟢 Easy | #70 |
| 2 | House Robber | 🟡 Medium | #198 |
| 3 | House Robber II | 🟡 Medium | #213 |
| 4 | Coin Change | 🟡 Medium | #322 |
| 5 | Word Break | 🟡 Medium | #139 |
| 6 | Decode Ways | 🟡 Medium | #91 |
| 7 | Longest Increasing Subsequence | 🟡 Medium | #300 |

> **Pattern to lock in:** State = "what do I need at position i?" Draw the recurrence before coding.

---

### Day 6 — Dynamic Programming: 2D + Sequences (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Unique Paths | 🟡 Medium | #62 |
| 2 | Longest Common Subsequence | 🟡 Medium | #1143 |
| 3 | Edit Distance | 🔴 Hard | #72 |
| 4 | Burst Balloons | 🔴 Hard | #312 |
| 5 | Maximum Profit in Job Scheduling | 🔴 Hard | #1235 |

---

### Day 7 — Week 1 Review + Mock

- Re-solve 3 problems you struggled with this week (from memory, no hints)
- **Timed mock:** 45 min · 1 medium + 1 hard · plain text editor
- Write BFS and DFS implementations from scratch

---

### Day 8 — Arrays + Hashmaps + Two Pointers (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Two Sum | 🟢 Easy | #1 |
| 2 | Contains Duplicate | 🟢 Easy | #217 |
| 3 | Product of Array Except Self | 🟡 Medium | #238 |
| 4 | Longest Consecutive Sequence | 🟡 Medium | #128 |
| 5 | 3Sum | 🟡 Medium | #15 |
| 6 | Container With Most Water | 🟡 Medium | #11 |
| 7 | Trapping Rain Water | 🔴 Hard | #42 |

---

### Day 9 — Sliding Window + Binary Search (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Longest Substring Without Repeating | 🟡 Medium | #3 |
| 2 | Longest Repeating Char Replacement | 🟡 Medium | #424 |
| 3 | Minimum Window Substring | 🔴 Hard | #76 |
| 4 | Search in Rotated Sorted Array | 🟡 Medium | #33 |
| 5 | Koko Eating Bananas | 🟡 Medium | #875 |
| 6 | Median of Two Sorted Arrays | 🔴 Hard | #4 |

---

### Day 10 — Heap (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Kth Largest Element in Array | 🟡 Medium | #215 |
| 2 | K Closest Points to Origin | 🟡 Medium | #973 |
| 3 | Task Scheduler | 🟡 Medium | #621 |
| 4 | Design Twitter | 🟡 Medium | #355 |
| 5 | Find Median from Data Stream | 🔴 Hard | #295 |
| 6 | Merge K Sorted Lists | 🔴 Hard | #23 |

---

### Day 11 — Stack + Intervals (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Valid Parentheses | 🟢 Easy | #20 |
| 2 | Daily Temperatures | 🟡 Medium | #739 |
| 3 | Largest Rectangle in Histogram | 🔴 Hard | #84 |
| 4 | Merge Intervals | 🟡 Medium | #56 |
| 5 | Non-overlapping Intervals | 🟡 Medium | #435 |
| 6 | Meeting Rooms II | 🟡 Medium | #253 |

---

### Day 12 — Backtracking + Trie (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Subsets | 🟡 Medium | #78 |
| 2 | Combination Sum | 🟡 Medium | #39 |
| 3 | Permutations | 🟡 Medium | #46 |
| 4 | Word Search | 🟡 Medium | #79 |
| 5 | Implement Trie | 🟡 Medium | #208 |
| 6 | Word Search II | 🔴 Hard | #212 |

---

### Day 13 — Linked List + Bit Manipulation (6 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Reverse Linked List | 🟢 Easy | #206 |
| 2 | Linked List Cycle | 🟢 Easy | #141 |
| 3 | Reorder List | 🟡 Medium | #143 |
| 4 | LRU Cache | 🟡 Medium | #146 |
| 5 | Missing Number | 🟢 Easy | #268 |
| 6 | Sum of Two Integers | 🟡 Medium | #371 |

---

### Day 14 — Full Mock Day

- **Session 1 (morning):** 45 min · 1 graph + 1 DP problem
- **Session 2 (afternoon):** 45 min · 1 tree + 1 hard
- Debrief after each: time complexity, edge cases, code quality
- Use new problems not solved before. Suggested: LeetCode Google-tagged, sorted by frequency.

---

---

<a id="plan-5"></a>
# PLAN 5 — 2 Weeks / 150 Questions

> **Intensity:** 10–11 problems/day · 4–5 hrs/day  
> **Coverage:** Full NeetCode 150 — all rounds, high confidence  
> **Strategy:** Topic-concentrated days. Hardest topics (graphs, DP) in Week 1 while fresh.

---

### Day 1 — Graphs: BFS/DFS + Topo (10 problems)

**BFS/DFS (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Number of Islands | 🟡 Medium | #200 |
| 2 | Clone Graph | 🟡 Medium | #133 |
| 3 | Rotting Oranges | 🟡 Medium | #994 |
| 4 | Pacific Atlantic Water Flow | 🟡 Medium | #417 |
| 5 | Surrounded Regions | 🟡 Medium | #130 |
| 6 | Word Ladder | 🔴 Hard | #127 |

**Topo + Union Find (4)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 7 | Course Schedule | 🟡 Medium | #207 |
| 8 | Course Schedule II | 🟡 Medium | #210 |
| 9 | Redundant Connection | 🟡 Medium | #684 |
| 10 | Alien Dictionary | 🔴 Hard | #269 |

---

### Day 2 — Graphs cont. + Trees I (10 problems)

**Graphs (4)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Number of Connected Components | 🟡 Medium | #323 |
| 2 | Accounts Merge | 🟡 Medium | #721 |
| 3 | Graph Valid Tree | 🟡 Medium | #261 |
| 4 | Word Ladder II | 🔴 Hard | #126 |

**Trees — DFS (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 5 | Invert Binary Tree | 🟢 Easy | #226 |
| 6 | Max Depth of Binary Tree | 🟢 Easy | #104 |
| 7 | Diameter of Binary Tree | 🟢 Easy | #543 |
| 8 | Validate BST | 🟡 Medium | #98 |
| 9 | Lowest Common Ancestor | 🟡 Medium | #236 |
| 10 | Binary Tree Max Path Sum | 🔴 Hard | #124 |

---

### Day 3 — Trees II + Heap (11 problems)

**Trees — BFS + Advanced (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Binary Tree Level Order Traversal | 🟡 Medium | #102 |
| 2 | Binary Tree Right Side View | 🟡 Medium | #199 |
| 3 | Construct Tree from Pre+Inorder | 🟡 Medium | #105 |
| 4 | Kth Smallest in BST | 🟡 Medium | #230 |
| 5 | Serialize / Deserialize Binary Tree | 🔴 Hard | #297 |

**Heap (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 6 | Kth Largest Element in Array | 🟡 Medium | #215 |
| 7 | K Closest Points to Origin | 🟡 Medium | #973 |
| 8 | Task Scheduler | 🟡 Medium | #621 |
| 9 | Design Twitter | 🟡 Medium | #355 |
| 10 | Find Median from Data Stream | 🔴 Hard | #295 |
| 11 | Merge K Sorted Lists | 🔴 Hard | #23 |

---

### Day 4 — Dynamic Programming: 1D + Stocks (11 problems)

**DP — 1D (8)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Climbing Stairs | 🟢 Easy | #70 |
| 2 | House Robber | 🟡 Medium | #198 |
| 3 | House Robber II | 🟡 Medium | #213 |
| 4 | Coin Change | 🟡 Medium | #322 |
| 5 | Coin Change II | 🟡 Medium | #518 |
| 6 | Decode Ways | 🟡 Medium | #91 |
| 7 | Word Break | 🟡 Medium | #139 |
| 8 | Longest Increasing Subsequence | 🟡 Medium | #300 |

**DP — Stocks (3)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 9 | Best Time to Buy/Sell with Cooldown | 🟡 Medium | #309 |
| 10 | Best Time to Buy/Sell III | 🔴 Hard | #123 |
| 11 | Best Time to Buy/Sell IV | 🔴 Hard | #188 |

---

### Day 5 — Dynamic Programming: 2D + Advanced (10 problems)

**DP — 2D (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Unique Paths | 🟡 Medium | #62 |
| 2 | Longest Common Subsequence | 🟡 Medium | #1143 |
| 3 | Edit Distance | 🔴 Hard | #72 |
| 4 | Maximal Square | 🟡 Medium | #221 |
| 5 | Distinct Subsequences | 🔴 Hard | #115 |

**DP — Advanced (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 6 | Partition Equal Subset Sum | 🟡 Medium | #416 |
| 7 | Target Sum | 🟡 Medium | #494 |
| 8 | Burst Balloons | 🔴 Hard | #312 |
| 9 | Regular Expression Matching | 🔴 Hard | #10 |
| 10 | Maximum Profit in Job Scheduling | 🔴 Hard | #1235 |

---

### Day 6 — Arrays + Two Pointers + Sliding Window (11 problems)

**Arrays + Hashmaps (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Two Sum | 🟢 Easy | #1 |
| 2 | Contains Duplicate | 🟢 Easy | #217 |
| 3 | Product of Array Except Self | 🟡 Medium | #238 |
| 4 | Top K Frequent Elements | 🟡 Medium | #347 |
| 5 | Longest Consecutive Sequence | 🟡 Medium | #128 |

**Two Pointers + Sliding Window (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 6 | 3Sum | 🟡 Medium | #15 |
| 7 | Container With Most Water | 🟡 Medium | #11 |
| 8 | Trapping Rain Water | 🔴 Hard | #42 |
| 9 | Longest Substring Without Repeating | 🟡 Medium | #3 |
| 10 | Minimum Window Substring | 🔴 Hard | #76 |
| 11 | Sliding Window Maximum | 🔴 Hard | #239 |

---

### Day 7 — Week 1 Review + Mock

- Re-solve your hardest graph problem and hardest DP problem from memory
- **Timed mock:** 45 min · 1 graph + 1 DP · plain text editor

---

### Day 8 — Binary Search + Stack (10 problems)

**Binary Search (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Search in Rotated Sorted Array | 🟡 Medium | #33 |
| 2 | Find Minimum in Rotated Array | 🟡 Medium | #153 |
| 3 | Koko Eating Bananas | 🟡 Medium | #875 |
| 4 | Time Based Key-Value Store | 🟡 Medium | #981 |
| 5 | Median of Two Sorted Arrays | 🔴 Hard | #4 |

**Stack (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 6 | Valid Parentheses | 🟢 Easy | #20 |
| 7 | Min Stack | 🟡 Medium | #155 |
| 8 | Daily Temperatures | 🟡 Medium | #739 |
| 9 | Car Fleet | 🟡 Medium | #853 |
| 10 | Largest Rectangle in Histogram | 🔴 Hard | #84 |

---

### Day 9 — Linked List + Intervals (11 problems)

**Linked List (6)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Reverse Linked List | 🟢 Easy | #206 |
| 2 | Merge Two Sorted Lists | 🟢 Easy | #21 |
| 3 | Linked List Cycle | 🟢 Easy | #141 |
| 4 | Reorder List | 🟡 Medium | #143 |
| 5 | Remove Nth Node From End | 🟡 Medium | #19 |
| 6 | LRU Cache | 🟡 Medium | #146 |

**Intervals (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 7 | Insert Interval | 🟡 Medium | #57 |
| 8 | Merge Intervals | 🟡 Medium | #56 |
| 9 | Non-overlapping Intervals | 🟡 Medium | #435 |
| 10 | Meeting Rooms II | 🟡 Medium | #253 |
| 11 | Minimum Interval to Include Each Query | 🔴 Hard | #1851 |

---

### Day 10 — Backtracking (7 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Subsets | 🟡 Medium | #78 |
| 2 | Subsets II | 🟡 Medium | #90 |
| 3 | Combination Sum | 🟡 Medium | #39 |
| 4 | Combination Sum II | 🟡 Medium | #40 |
| 5 | Permutations | 🟡 Medium | #46 |
| 6 | Word Search | 🟡 Medium | #79 |
| 7 | N-Queens | 🔴 Hard | #51 |

> **Pattern to lock in:** choose → recurse → unchoose. Always the same 3 lines.

---

### Day 11 — Trie + Bit Manipulation (8 problems)

**Trie (3)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Implement Trie | 🟡 Medium | #208 |
| 2 | Design Add and Search Words | 🟡 Medium | #211 |
| 3 | Word Search II | 🔴 Hard | #212 |

**Bit Manipulation (5)**

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 4 | Number of 1 Bits | 🟢 Easy | #191 |
| 5 | Counting Bits | 🟢 Easy | #338 |
| 6 | Missing Number | 🟢 Easy | #268 |
| 7 | Reverse Bits | 🟢 Easy | #190 |
| 8 | Sum of Two Integers | 🟡 Medium | #371 |

---

### Day 12 — Google-tagged extras + Greedy (8 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Jump Game II | 🟡 Medium | #45 |
| 2 | Gas Station | 🟡 Medium | #134 |
| 3 | Partition Labels | 🟡 Medium | #763 |
| 4 | Hand of Straights | 🟡 Medium | #846 |
| 5 | Merge Triplets to Form Target | 🟡 Medium | #1899 |
| 6 | Valid Parenthesis String | 🟡 Medium | #678 |
| 7 | Group Anagrams | 🟡 Medium | #49 |
| 8 | Encode and Decode Strings | 🟡 Medium | #271 |

---

### Day 13 — Speed Drill + Weak Spots (10 problems)

- Identify your 2 weakest topics from Week 1 + Days 8–12
- Do 5 problems per topic under 20-min timer each
- No looking up solutions mid-problem

---

### Day 14 — Full Mock Day

- **Session 1 (morning):** 45 min · 1 medium + 1 hard · plain text editor · no IDE
- **Session 2 (afternoon):** 45 min · 1 medium + 1 hard
- Debrief after each: time/space complexity, edge cases, production-quality code

---

---

<a id="plan-6"></a>
# PLAN 6 — 4 Weeks / 150 Questions

> **Intensity:** 5 problems/day · 1.5–2 hrs/day  
> **Coverage:** Full NeetCode 150, complete preparation with review and mocks built in  
> **Strategy:** Even pacing. Review day every week. Mock sessions at end of weeks 2, 3, 4.

---

## Week 1 — Foundation: Arrays, Sliding Window, Stack, Binary Search, Intervals

### Day 1 — Arrays + Hashmaps (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Two Sum | 🟢 Easy | #1 |
| 2 | Contains Duplicate | 🟢 Easy | #217 |
| 3 | Valid Anagram | 🟢 Easy | #242 |
| 4 | Group Anagrams | 🟡 Medium | #49 |
| 5 | Top K Frequent Elements | 🟡 Medium | #347 |

### Day 2 — Arrays cont. + Two Pointers (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Product of Array Except Self | 🟡 Medium | #238 |
| 2 | Longest Consecutive Sequence | 🟡 Medium | #128 |
| 3 | 3Sum | 🟡 Medium | #15 |
| 4 | Container With Most Water | 🟡 Medium | #11 |
| 5 | Trapping Rain Water | 🔴 Hard | #42 |

### Day 3 — Sliding Window (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Best Time to Buy/Sell Stock | 🟢 Easy | #121 |
| 2 | Longest Substring Without Repeating | 🟡 Medium | #3 |
| 3 | Longest Repeating Char Replacement | 🟡 Medium | #424 |
| 4 | Minimum Window Substring | 🔴 Hard | #76 |
| 5 | Sliding Window Maximum | 🔴 Hard | #239 |

### Day 4 — Stack (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Valid Parentheses | 🟢 Easy | #20 |
| 2 | Min Stack | 🟡 Medium | #155 |
| 3 | Daily Temperatures | 🟡 Medium | #739 |
| 4 | Car Fleet | 🟡 Medium | #853 |
| 5 | Largest Rectangle in Histogram | 🔴 Hard | #84 |

### Day 5 — Binary Search (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Binary Search | 🟢 Easy | #704 |
| 2 | Search in Rotated Sorted Array | 🟡 Medium | #33 |
| 3 | Find Minimum in Rotated Array | 🟡 Medium | #153 |
| 4 | Koko Eating Bananas | 🟡 Medium | #875 |
| 5 | Median of Two Sorted Arrays | 🔴 Hard | #4 |

### Day 6 — Intervals + Linked List (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Merge Intervals | 🟡 Medium | #56 |
| 2 | Insert Interval | 🟡 Medium | #57 |
| 3 | Non-overlapping Intervals | 🟡 Medium | #435 |
| 4 | Meeting Rooms II | 🟡 Medium | #253 |
| 5 | Reverse Linked List | 🟢 Easy | #206 |

### Day 7 — Week 1 Review

- Re-solve 3 problems you struggled with this week from memory
- Write sliding window template and binary search template from scratch
- No new problems today

---

## Week 2 — Core DS: Linked List, Trees, Heap

### Day 8 — Linked List (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Merge Two Sorted Lists | 🟢 Easy | #21 |
| 2 | Linked List Cycle | 🟢 Easy | #141 |
| 3 | Reorder List | 🟡 Medium | #143 |
| 4 | Remove Nth Node From End | 🟡 Medium | #19 |
| 5 | LRU Cache | 🟡 Medium | #146 |

### Day 9 — Trees: Basic DFS (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Invert Binary Tree | 🟢 Easy | #226 |
| 2 | Max Depth of Binary Tree | 🟢 Easy | #104 |
| 3 | Diameter of Binary Tree | 🟢 Easy | #543 |
| 4 | Validate BST | 🟡 Medium | #98 |
| 5 | Binary Tree Right Side View | 🟡 Medium | #199 |

### Day 10 — Trees: BFS + BST (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Binary Tree Level Order Traversal | 🟡 Medium | #102 |
| 2 | Kth Smallest in BST | 🟡 Medium | #230 |
| 3 | Construct Tree from Pre+Inorder | 🟡 Medium | #105 |
| 4 | Lowest Common Ancestor | 🟡 Medium | #236 |
| 5 | Count Good Nodes in Tree | 🟡 Medium | #1448 |

### Day 11 — Trees: Advanced (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Path Sum III | 🟡 Medium | #437 |
| 2 | Binary Tree Zigzag Level Order | 🟡 Medium | #103 |
| 3 | Lowest Common Ancestor BST | 🟡 Medium | #235 |
| 4 | Binary Tree Max Path Sum | 🔴 Hard | #124 |
| 5 | Serialize / Deserialize Binary Tree | 🔴 Hard | #297 |

### Day 12 — Heap I (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Kth Largest Element in Array | 🟡 Medium | #215 |
| 2 | K Closest Points to Origin | 🟡 Medium | #973 |
| 3 | Top K Frequent Words | 🟡 Medium | #692 |
| 4 | Task Scheduler | 🟡 Medium | #621 |
| 5 | Design Twitter | 🟡 Medium | #355 |

### Day 13 — Heap II (4 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Find Median from Data Stream | 🔴 Hard | #295 |
| 2 | Merge K Sorted Lists | 🔴 Hard | #23 |
| 3 | Smallest Range Covering K Lists | 🔴 Hard | #632 |
| 4 | IPO (Greedy + Heap) | 🔴 Hard | #502 |

### Day 14 — Week 2 Review + Mock

- Re-solve hardest tree problem from memory
- Re-solve hardest heap problem from memory
- **Timed mock:** 45 min · 1 tree + 1 heap problem · plain text editor

---

## Week 3 — Advanced: Graphs + Dynamic Programming

### Day 15 — Graphs: BFS/DFS (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Number of Islands | 🟡 Medium | #200 |
| 2 | Rotting Oranges | 🟡 Medium | #994 |
| 3 | Pacific Atlantic Water Flow | 🟡 Medium | #417 |
| 4 | Walls and Gates | 🟡 Medium | #286 |
| 5 | Word Ladder | 🔴 Hard | #127 |

### Day 16 — Graphs: Topo + Union Find (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Course Schedule | 🟡 Medium | #207 |
| 2 | Course Schedule II | 🟡 Medium | #210 |
| 3 | Number of Connected Components | 🟡 Medium | #323 |
| 4 | Redundant Connection | 🟡 Medium | #684 |
| 5 | Alien Dictionary | 🔴 Hard | #269 |

### Day 17 — Graphs: Advanced (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Clone Graph | 🟡 Medium | #133 |
| 2 | Surrounded Regions | 🟡 Medium | #130 |
| 3 | Accounts Merge | 🟡 Medium | #721 |
| 4 | Graph Valid Tree | 🟡 Medium | #261 |
| 5 | Swim in Rising Water | 🔴 Hard | #778 |

### Day 18 — DP: 1D (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Climbing Stairs | 🟢 Easy | #70 |
| 2 | House Robber | 🟡 Medium | #198 |
| 3 | Coin Change | 🟡 Medium | #322 |
| 4 | Word Break | 🟡 Medium | #139 |
| 5 | Decode Ways | 🟡 Medium | #91 |

### Day 19 — DP: 1D cont. + Stocks (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | House Robber II | 🟡 Medium | #213 |
| 2 | Longest Increasing Subsequence | 🟡 Medium | #300 |
| 3 | Coin Change II | 🟡 Medium | #518 |
| 4 | Best Time to Buy/Sell with Cooldown | 🟡 Medium | #309 |
| 5 | Best Time to Buy/Sell III | 🔴 Hard | #123 |

### Day 20 — DP: 2D (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Unique Paths | 🟡 Medium | #62 |
| 2 | Longest Common Subsequence | 🟡 Medium | #1143 |
| 3 | Edit Distance | 🔴 Hard | #72 |
| 4 | Maximal Square | 🟡 Medium | #221 |
| 5 | Burst Balloons | 🔴 Hard | #312 |

### Day 21 — Week 3 Review + Mock

- Re-solve hardest graph problem from memory (topo sort from scratch — both DFS and BFS version)
- Re-solve hardest 2D DP from memory
- **Timed mock:** 45 min · 1 graph + 1 DP

---

## Week 4 — Polish: Backtracking, Trie, Greedy, Mocks

### Day 22 — Backtracking (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Subsets | 🟡 Medium | #78 |
| 2 | Combination Sum | 🟡 Medium | #39 |
| 3 | Permutations | 🟡 Medium | #46 |
| 4 | Word Search | 🟡 Medium | #79 |
| 5 | N-Queens | 🔴 Hard | #51 |

### Day 23 — Trie (3 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Implement Trie | 🟡 Medium | #208 |
| 2 | Design Add and Search Words | 🟡 Medium | #211 |
| 3 | Word Search II | 🔴 Hard | #212 |

### Day 24 — Bit Manipulation + Greedy (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Missing Number | 🟢 Easy | #268 |
| 2 | Number of 1 Bits | 🟢 Easy | #191 |
| 3 | Sum of Two Integers | 🟡 Medium | #371 |
| 4 | Jump Game II | 🟡 Medium | #45 |
| 5 | Gas Station | 🟡 Medium | #134 |

### Day 25 — DP: Advanced + Google Extras (5 problems)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Partition Equal Subset Sum | 🟡 Medium | #416 |
| 2 | Target Sum | 🟡 Medium | #494 |
| 3 | Regular Expression Matching | 🔴 Hard | #10 |
| 4 | Maximum Profit in Job Scheduling | 🔴 Hard | #1235 |
| 5 | Distinct Subsequences | 🔴 Hard | #115 |

### Day 26 — Speed Drill (8 problems, 20 min each)

Pick 8 unsolved mediums from NeetCode 150 or LeetCode Google-tagged.  
Goal: solve each in under 20 minutes. Timer on. No hints.

### Day 27 — Full Mock Interview #1

- 45 min · 1 medium + 1 hard
- Code in plain text editor (Google Docs or VS Code with no IntelliSense)
- Speak every thought out loud
- After: self-grade on code cleanliness, edge cases, complexity explanation

### Day 28 — Full Mock Interview #2

- 45 min · 1 medium + 1 hard · entirely new problems
- Simulate onsite pressure: back-to-back if possible with a 10-min break

### Day 29 — Weak Spot Targeting

- Look back at every problem you failed, went over time, or needed hints
- Re-solve the worst 4–5 from scratch
- Then solve them again 2 hours later with no reference

### Day 30 — Final Day

- Review Python heap/graph/DP templates from memory only
- 2–3 easy warm-up problems
- No new hard problems
- Rest

---

---

## References

- [NeetCode 150](https://neetcode.io/practice) — primary problem list
- [Blind 75](https://neetcode.io/practice/blind75) — fallback if time runs short
- [LeetCode Google-tagged](https://leetcode.com/company/google/) — supplement for days marked "Google extras"
- [Real L4 experience — Medium 2025](https://medium.com/@shreyagupta_17295/google-interview-experience-l4-c5908bde5aa0)
- [LeetCode Discuss — L4 India offer post](https://leetcode.com/discuss/post/6479658)
- [IGotAnOffer — Google L4 guide](https://igotanoffer.com/en/advice/google-l4-interview)

