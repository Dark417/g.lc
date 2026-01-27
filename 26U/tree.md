# Tree

## Category

### Medium
- [M] [236. Lowest Common Ancestor of a Binary Tree](#lc-0236)\
  Find the lowest common ancestor of two nodes in a binary tree.\
  `Tree` `Depth-First Search` `Binary Tree`

### Hard
- [H] [124. Binary Tree Maximum Path Sum](#lc-0124)\
  Find the maximum path sum in a binary tree.\
  `Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`

  - [H] [2538. Difference Between Maximum and Minimum Price Sum](#lc-2538)\
    Max difference of subtree price sums.\
    `Tree` `Depth-First Search` `Dynamic Programming`

- [H] [297. Serialize and Deserialize Binary Tree](#lc-0297)\
  Design an algorithm to serialize and deserialize a binary tree.\
  `Tree` `Depth-First Search` `Breadth-First Search` `Design`

- [H] [968. Binary Tree Cameras](#lc-0968)\
  Minimum cameras to monitor all nodes.\
  `Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`

- [H] [987. Vertical Order Traversal of a Binary Tree](#lc-0987)\
  Return the vertical order traversal of a binary tree's values.\
  `Tree` `Depth-First Search` `Breadth-First Search` `Hash Table`

- [H] [1028. Recover a Tree From Preorder Traversal](#lc-1028)\
  Recover a binary tree from its preorder traversal string.\
  `Tree` `Depth-First Search` `String`

- [H] [1483. Kth Ancestor of a Tree Node](#lc-1483)\
  Find the kth ancestor of a given node.\
  `Bit Manipulation` `Tree` `Depth-First Search` `Breadth-First Search`

- [H] [2603. Collect Coins in a Tree](#lc-2603)\
  Minimum edges to traverse to collect all coins and return to start.\
  `Tree` `Graph` `Topological Sort` `Array`

- [H] [2791. Count Paths That Can Form a Palindrome in a Tree](#lc-2791)\
  Count paths whose character sequence can form a palindrome.\
  `Bit Manipulation` `Tree` `Depth-First Search` `Dynamic Programming`

- [H] [2872. Maximum Number of K-Divisible Components](#lc-2872)\
  Maximum components where each has sum divisible by k.\
  `Tree` `Depth-First Search`

- [H] [3562. Maximum Profit from Trading Stocks with Discounts](#lc-3562)\
  Maximum profit trading stocks on a tree with discounts.\
  `Tree` `Depth-First Search` `Array` `Dynamic Programming`

- [H] [LCR 051. 二叉树中的最大路径和](#lc-lcr-051)\
  求二叉树中的最大路径和.\
  `Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`

## Solutions (Python)

<a id="lc-0124"></a>
#### 124. [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) [H]
`Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
Description: Find the maximum path sum in a binary tree where any node can be the start or end.

```python
class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        res = -inf
        def dfs(node):
            if node is None:
                return 0
            l = dfs(node.left)
            r = dfs(node.right)
            nonlocal res
            res = max(res, l + r + node.val)
            return max(max(l, r) + node.val, 0)
        dfs(root)
        return res


class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        if not root:
            return float("-inf")

        best = float("-inf")
        gain = {None: 0}
        stack = [(root, 0)]  # 0=enter, 1=exit

        while stack:
            node, state = stack.pop()
            if not node:
                continue
            if state == 0:
                stack.append((node, 1))
                stack.append((node.right, 0))
                stack.append((node.left, 0))
            else:
                left = max(0, gain[node.left])
                right = max(0, gain[node.right])
                best = max(best, node.val + left + right)
                gain[node] = node.val + max(left, right)

        return best
```

<a id="lc-2538"></a>
#### 2538. [Difference Between Maximum and Minimum Price Sum](https://leetcode.com/problems/difference-between-maximum-and-minimum-price-sum/) [H]
`Tree` `Depth-First Search` `Dynamic Programming`
Description: Unrooted tree with prices. For each node as root, cost = max path sum − min path sum (min is always just the root itself). Return the max cost.

##### Approach 1: Tree diameter variant
Idea: For any path, answer = path_sum − min_endpoint_price. Track two chains per node: one including the far-end leaf price, one excluding it. Combine like tree diameter.

```python
class Solution:
    def maxOutput(self, n: int, edges: List[List[int]], price: List[int]) -> int:
        g = [[] for _ in range(n)]
        for x, y in edges:
            g[x].append(y)
            g[y].append(x)  # 建树

        ans = 0
        def dfs(x: int, fa: int) -> (int, int):
            nonlocal ans
            max_s1 = p = price[x]
            max_s2 = 0
            for y in g[x]:
                if y == fa: continue
                s1, s2 = dfs(y, x)
                # 前面最大带叶子的路径和 + 当前不带叶子的路径和
                # 前面最大不带叶子的路径和 + 当前带叶子的路径和
                ans = max(ans, max_s1 + s2, max_s2 + s1)
                max_s1 = max(max_s1, s1 + p)
                max_s2 = max(max_s2, s2 + p)  # 这里加上 p 是因为 x 必然不是叶子
            return max_s1, max_s2
        dfs(0, -1)
        return ans
# Time: O(n), Space: O(n)

class Solution:
    def maxOutput(self, n: int, edges: List[List[int]], price: List[int]) -> int:
        from collections import defaultdict

        # Build adjacency list
        graph = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        ans = 0

        def dfs(u: int, parent: int):
            """
            Returns:
              mx: maximum downward path sum starting at u
              mn: minimum downward path sum starting at u
            """
            nonlocal ans

            # Base values: path consisting of only node u
            max_down = price[u]
            min_down = price[u]

            for v in graph[u]:
                if v == parent:
                    continue

                child_max, child_min = dfs(v, u)

                # Either extend child's path or stop at u
                max_down = max(max_down, price[u] + child_max)
                min_down = min(min_down, price[u] + child_min)

            # Update global answer
            ans = max(ans, max_down - min_down)

            return max_down, min_down

        dfs(0, -1)
        return ans
```

<a id="lc-0236"></a>
#### 236. [Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) [M]
`Tree` `Depth-First Search` `Binary Tree`
Description: Find the lowest common ancestor of two given nodes in a binary tree.

##### Approach 1: Recursive DFS
Idea: Recursively search left and right subtrees; if both return non-null, current node is the LCA.

```python
class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        if not root:
            return None
        if root == p or root == q:
            return root
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        if left and right:
            return root
        return left if left else right
# Time: O(n), Space: O(n)
```

<a id="lc-0297"></a>
#### 297. [Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) [H]
`Tree` `Depth-First Search` `Breadth-First Search` `Design`
Description: Design an algorithm to serialize and deserialize a binary tree.

##### Approach 1: Preorder DFS
Idea: Preorder traversal with `N` for null nodes. Deserialize by consuming tokens left-to-right recursively.

```python
class Codec:
    def serialize(self, root):
        res = []
        def dfs(node):
            if not node:
                res.append('N')
                return
            res.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ','.join(res)

    def deserialize(self, data):
        vals = iter(data.split(','))
        def dfs():
            v = next(vals)
            if v == 'N':
                return None
            node = TreeNode(int(v))
            node.left = dfs()
            node.right = dfs()
            return node
        return dfs()
# Time: O(n), Space: O(n)
```

##### Approach 2: BFS (level-order)
Idea: BFS serialization using `N` for nulls. Deserialize with a queue pairing parents with children.

```python
class Codec:
    def serialize(self, root):
        if not root:
            return 'N'
        res = []
        q = deque([root])
        while q:
            node = q.popleft()
            if not node:
                res.append('N')
            else:
                res.append(str(node.val))
                q.append(node.left)
                q.append(node.right)
        return ','.join(res)

    def deserialize(self, data):
        vals = data.split(',')
        if vals[0] == 'N':
            return None
        root = TreeNode(int(vals[0]))
        q = deque([root])
        i = 1
        while q:
            node = q.popleft()
            if vals[i] != 'N':
                node.left = TreeNode(int(vals[i]))
                q.append(node.left)
            i += 1
            if vals[i] != 'N':
                node.right = TreeNode(int(vals[i]))
                q.append(node.right)
            i += 1
        return root
# Time: O(n), Space: O(n)
```

<a id="lc-0968"></a>
#### 968. [Binary Tree Cameras](https://leetcode.com/problems/binary-tree-cameras/) [H]
`Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
Description: Find the minimum number of cameras needed to monitor all nodes in a binary tree.

##### Approach 1: Greedy DFS (3 states)
Idea: Post-order DFS. Each node returns a state: 0 = not covered, 1 = has camera, 2 = covered. Place camera greedily at parent of uncovered child.

```python
class Solution:
    def minCameraCover(self, root: Optional[TreeNode]) -> int:
        ans = 0
        def dfs(node):
            nonlocal ans
            if not node:
                return 2
            l = dfs(node.left)
            r = dfs(node.right)
            if l == 0 or r == 0:
                ans += 1
                return 1
            if l == 1 or r == 1:
                return 2
            return 0
        if dfs(root) == 0:
            ans += 1
        return ans
# Time: O(n), Space: O(h)
```

##### Approach 2: Tree DP
Idea: dp[node] = (no_cam_covered, has_cam, not_covered). Minimise cameras at each subtree.

```python
class Solution:
    def minCameraCover(self, root: Optional[TreeNode]) -> int:
        def dfs(node):
            # returns (min cameras if node covered but no camera here,
            #          min cameras if node has camera,
            #          min cameras if node not covered)
            if not node:
                return 0, inf, 0
            la, lb, lc = dfs(node.left)
            ra, rb, rc = dfs(node.right)
            # node has camera: children can be in any state
            b = 1 + min(la, lb, lc) + min(ra, rb, rc)
            # node covered, no camera: at least one child must have camera
            a = min(lb + min(ra, rb), rb + min(la, lb))
            # node not covered: children must be covered (no camera here)
            c = la + ra
            return a, b, c
        a, b, _ = dfs(root)
        return min(a, b)
# Time: O(n), Space: O(h)
```

<a id="lc-0987"></a>
#### 987. [Vertical Order Traversal of a Binary Tree](https://leetcode.com/problems/vertical-order-traversal-of-a-binary-tree/) [H]
`Tree` `Depth-First Search` `Breadth-First Search` `Hash Table`
Description: Return the vertical order traversal of a binary tree's values.

##### Approach 1: DFS + sort
Idea: DFS collecting (col, row, val) triples. Sort by col, then row, then val. Group by col.

```python
class Solution:
    def verticalTraversal(self, root: Optional[TreeNode]) -> List[List[int]]:
        nodes = []
        def dfs(node, row, col):
            if not node:
                return
            nodes.append((col, row, node.val))
            dfs(node.left, row + 1, col - 1)
            dfs(node.right, row + 1, col + 1)
        dfs(root, 0, 0)
        nodes.sort()
        res = []
        prev_col = -inf
        for col, _, val in nodes:
            if col != prev_col:
                res.append([])
                prev_col = col
            res[-1].append(val)
        return res
# Time: O(n log n), Space: O(n)
```

<a id="lc-1028"></a>
#### 1028. [Recover a Tree From Preorder Traversal](https://leetcode.com/problems/recover-a-tree-from-preorder-traversal/) [H]
Description: Recover a binary tree from a string like `"1-2--3--4-5--6--7"` where dash count = depth.

##### Approach 1: Stack
Idea: Parse depth (dash count) and value. Use a stack to track the path from root to current node. Pop until stack size matches depth, then attach as left or right child.

```python
class Solution:
    def recoverFromPreorder(self, traversal: str) -> Optional[TreeNode]:
        st = []
        i, n = 0, len(traversal)
        while i < n:
            depth = 0
            while i < n and traversal[i] == '-':
                depth += 1
                i += 1
            val = 0
            while i < n and traversal[i].isdigit():
                val = val * 10 + int(traversal[i])
                i += 1
            node = TreeNode(val)
            while len(st) > depth:
                st.pop()
            if st:
                if not st[-1].left:
                    st[-1].left = node
                else:
                    st[-1].right = node
            st.append(node)
        return st[0]
# Time: O(n), Space: O(h)
```

<a id="lc-1483"></a>
#### 1483. [Kth Ancestor of a Tree Node](https://leetcode.com/problems/kth-ancestor-of-a-tree-node/) [H]
`Bit Manipulation` `Tree` `Depth-First Search` `Breadth-First Search`
Description: Find the kth ancestor of a given node in a tree.

##### Approach 1: Binary lifting
Idea: Precompute `pa[i][x]` = 2^i-th ancestor of x. To find k-th ancestor, decompose k into binary and jump.

```python
class TreeAncestor:
    def __init__(self, n: int, parent: List[int]):
        LOG = max(1, n.bit_length())
        pa = [parent[:]]
        for _ in range(LOG - 1):
            nxt = [-1] * n
            for x in range(n):
                p = pa[-1][x]
                nxt[x] = pa[-1][p] if p != -1 else -1
            pa.append(nxt)
        self.pa = pa

    def getKthAncestor(self, node: int, k: int) -> int:
        for i in range(len(self.pa)):
            if (k >> i) & 1:
                node = self.pa[i][node]
                if node == -1:
                    break
        return node
# Time: init O(n log n), query O(log n). Space: O(n log n)
```

<a id="lc-2603"></a>
#### 2603. [Collect Coins in a Tree](https://leetcode.com/problems/collect-coins-in-a-tree/) [H]
`Tree` `Graph` `Topological Sort` `Array`
Description: Find the minimum number of edges to traverse to collect all coins and return to start.

##### Approach 1: Topological sort (prune leaves)
Idea: 1) Remove leaves without coins iteratively. 2) Remove 2 more layers (coins reachable from distance 2). 3) Answer = 2 × remaining edges.

```python
class Solution:
    def collectTheCoins(self, coins: List[int], edges: List[List[int]]) -> int:
        n = len(coins)
        g = [set() for _ in range(n)]
        for u, v in edges:
            g[u].add(v)
            g[v].add(u)
        # Phase 1: prune coinless leaves
        q = [i for i in range(n) if len(g[i]) == 1 and not coins[i]]
        for u in q:
            for v in g[u]:
                g[v].discard(u)
                if len(g[v]) == 1 and not coins[v]:
                    q.append(v)
            g[u].clear()
        # Phase 2: prune 2 layers of remaining leaves
        for _ in range(2):
            leaves = [i for i in range(n) if len(g[i]) == 1]
            for u in leaves:
                for v in g[u]:
                    g[v].discard(u)
                g[u].clear()
        return sum(len(g[i]) for i in range(n))
# Time: O(n), Space: O(n)
```

<a id="lc-2791"></a>
#### 2791. [Count Paths That Can Form a Palindrome in a Tree](https://leetcode.com/problems/count-paths-that-can-form-a-palindrome-in-a-tree/) [H]
`Bit Manipulation` `Tree` `Depth-First Search` `Dynamic Programming`
Description: Count paths in a tree whose character labels can be rearranged to form a palindrome.

##### Approach 1: XOR bitmask + DFS
Idea: Represent char parity as bitmask. Path u→v = mask[u] ⊕ mask[v]. Palindrome iff at most 1 bit set. Count matching pairs with a hash map.

```python
class Solution:
    def countPalindromePaths(self, parent: List[int], s: str) -> int:
        n = len(parent)
        g = [[] for _ in range(n)]
        for i in range(1, n):
            g[parent[i]].append((i, 1 << (ord(s[i]) - ord('a'))))
        cnt = defaultdict(int)
        cnt[0] = 1
        ans = 0
        st = [0]
        mask = [0] * n
        while st:
            u = st.pop()
            for v, w in g[u]:
                mask[v] = mask[u] ^ w
                ans += cnt[mask[v]]
                for k in range(26):
                    ans += cnt[mask[v] ^ (1 << k)]
                cnt[mask[v]] += 1
                st.append(v)
        return ans
# Time: O(26n), Space: O(n)
```

<a id="lc-2872"></a>
#### 2872. [Maximum Number of K-Divisible Components](https://leetcode.com/problems/maximum-number-of-k-divisible-components/) [H]
`Tree` `Depth-First Search`
Description: Split a tree into the maximum number of components where each has sum divisible by k.

##### Approach 1: Greedy DFS
Idea: DFS returns subtree sum. Whenever a subtree sum is divisible by k, cut it off (return 0) and increment the count.

```python
class Solution:
    def maxKDivisibleComponents(self, n: int, edges: List[List[int]], values: List[int], k: int) -> int:
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        ans = 0
        def dfs(u, fa):
            nonlocal ans
            s = values[u]
            for v in g[u]:
                if v != fa:
                    s += dfs(v, u)
            if s % k == 0:
                ans += 1
                return 0
            return s
        dfs(0, -1)
        return ans
# Time: O(n), Space: O(n)
```

<a id="lc-3562"></a>
#### 3562. [Maximum Profit from Trading Stocks with Discounts](https://leetcode.com/problems/maximum-profit-from-trading-stocks-with-discounts/) [H]
`Tree` `Depth-First Search` `Array` `Dynamic Programming`
Description: Maximize profit from trading stocks on a tree structure with parent-child discounts.

<a id="lc-lcr-051"></a>
#### LCR 051. [二叉树中的最大路径和](https://leetcode.cn/problems/jC7MId/) [H]
`Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
Description: 求二叉树中的最大路径和（同 [124](#lc-0124) 题，解法相同）。
