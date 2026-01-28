# Tree

## Category

### Easy
- [E] [100. Same Tree](#lc-0100)\
  Check if two binary trees are identical.\
  `Tree` `Depth-First Search` `Binary Tree`

- [E] [104. Maximum Depth of Binary Tree](#lc-0104)\
  Compute the maximum depth of a binary tree.\
  `Tree` `Depth-First Search` `Breadth-First Search`

- [E] [111. Minimum Depth of Binary Tree](#lc-0111)\
  Find the minimum depth from the root node to the closest leaf.\
  `Tree` `Depth-First Search` `Breadth-First Search`

- [E] [226. Invert Binary Tree](#lc-0226)\
  Swap left and right children for every node.\
  `Tree` `Depth-First Search` `Breadth-First Search`

- [E] [572. Subtree of Another Tree](#lc-0572)\
  Check if one tree is a subtree of another.\
  `Tree` `Depth-First Search` `Hash Table`

### Medium
- [M] [98. Validate Binary Search Tree](#lc-0098)\
  Verify the BST ordering property of a binary tree.\
  `Tree` `Depth-First Search` `Binary Search Tree`

- [M] [102. Binary Tree Level Order Traversal](#lc-0102)\
  Return tree nodes level by level.\
  `Tree` `Breadth-First Search` `Queue`

- [M] [103. Binary Tree Zigzag Level Order Traversal](#lc-0103)\
  Return zigzag level order traversal.\
  `Tree` `Breadth-First Search` `Queue`

- [M] [105. Construct Binary Tree From Preorder And Inorder Traversal](#lc-0105)\
  Reconstruct a tree from preorder and inorder traversals.\
  `Tree` `Array` `Hash Table` `Depth-First Search`

- [M] [106. Construct Binary Tree From Inorder And Postorder Traversal](#lc-0106)\
  Reconstruct a tree from inorder and postorder traversals.\
  `Tree` `Array` `Hash Table` `Depth-First Search`

- [M] [107. Binary Tree Level Order Traversal II](#lc-0107)\
  Return level order traversal in reverse.\
  `Tree` `Breadth-First Search` `Queue`

- [M] [116. Populating Next Right Pointers In Each Node](#lc-0116)\
  Fill the next pointer for each node to point to its right sibling.\
  `Tree` `Breadth-First Search` `Linked List` `Binary Tree`

- [M] [117. Populating Next Right Pointers in Each Node II](#lc-0117)\
  Connect each node to the next node on its level when the tree is not perfect.\
  `Tree` `Breadth-First Search` `Linked List`

- [M] [199. Binary Tree Right Side View](#lc-0199)\
  Return the rightmost node at each level.\
  `Tree` `Depth-First Search` `Breadth-First Search` `Queue`

- [M] [230. Kth Smallest Element In a Bst](#lc-0230)\
  Find the kth smallest value in a BST.\
  `Tree` `Depth-First Search` `Binary Search Tree` `Stack`

- [M] [236. Lowest Common Ancestor of a Binary Tree](#lc-0236)\
  Find the lowest common ancestor of two nodes in a binary tree.\
  `Tree` `Depth-First Search` `Binary Tree`

### Hard
- [H] [95. Unique Binary Search Trees II](#lc-0095)\
  Generate all structurally unique BSTs with n nodes.\
  `Tree` `Backtracking` `Binary Search Tree` `Dynamic Programming`

- [H] [96. Unique Binary Search Trees](#lc-0096)\
  Count the number of structurally unique BSTs with n nodes.\
  `Tree` `Dynamic Programming` `Binary Search Tree` `Math`

- [H] [429. N-ary Tree Level Order Traversal](#lc-0429)\
  Return level order traversal of an n-ary tree.\
  `Tree` `Breadth-First Search` `Queue`
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

- [H] [LCR 413. Substructure Determination](#lc-lcr-413)\
  Check if a binary tree B is a substructure of tree A.\
  `Tree` `Depth-First Search` `Binary Tree`

## Solutions (Python)
###
### Easy
111. 二叉树的最小深度
<a id="lc-0111"></a>
#### 111. [Minimum Depth of Binary Tree](https://leetcode.com/problems/minimum-depth-of-binary-tree/) [E]

```python
class Solution:
    def minDepth(self, root: Optional[TreeNode]) -> int:
        ans = inf
        def dfs(node: Optional[TreeNode], cnt: int) -> None:
            if node is None:
                return
            nonlocal ans
            cnt += 1
            if cnt >= ans:
                return  # 最优性剪枝
            if node.left is None and node.right is None:  # node 是叶子
                ans = cnt
                return
            dfs(node.left, cnt)
            dfs(node.right, cnt)
        dfs(root, 0)
        return ans if root else 0


class Solution:
    def minDepth(self, root: Optional[TreeNode]) -> int:
        ans = inf
        def dfs(node: Optional[TreeNode], cnt: int) -> None:
            if node is None:
                return
            cnt += 1
            if node.left is None and node.right is None:  # node 是叶子
                nonlocal ans
                ans = min(ans, cnt)
                return
            dfs(node.left, cnt)
            dfs(node.right, cnt)
        dfs(root, 0)
        return ans if root else 0

```

104. 二叉树的最大深度
```python
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        l_depth = self.maxDepth(root.left)
        r_depth = self.maxDepth(root.right)
        return max(l_depth, r_depth) + 1

# 方法二：自顶向下
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        ans = 0
        def dfs(node: Optional[TreeNode], depth: int) -> None:
            if node is None:
                return
            depth += 1
            nonlocal ans
            ans = max(ans, depth)
            dfs(node.left, depth)
            dfs(node.right, depth)
        dfs(root, 0)
        return ans
```



---
### Medium
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

<a id="lc-0106"></a>
#### 106. [Construct Binary Tree from Inorder and Postorder Traversal](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/) [M]
`Tree` `Array` `Hash Table` `Depth-First Search`
Description: Construct a binary tree from its inorder and postorder traversals.

##### Approach 1: Recursive with hash map
Idea: Root is the last element of postorder. Find root in inorder to split subtrees. Recursively build left and right.

```python
!!!
class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        def build(left, right):
            if left > right:
                return None
            val = postorder.pop()
            root = TreeNode(val)
            i = idx[val]
            root.right = build(i + 1, right)
            root.left = build(left, i - 1)
            return root
            
        idx = {val: i for i, val in enumerate(inorder)}
        return build(0, len(inorder) - 1)


class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        index = {x: i for i, x in enumerate(inorder)}

        def dfs(in_l: int, post_l: int, post_r: int) -> Optional[TreeNode]:
            if post_l == post_r:  # 空节点
                return None
            left_size = index[postorder[post_r - 1]] - in_l  # 左子树的大小
            print(left_size) #1
            left = dfs(in_l, post_l, post_l + left_size)
            right = dfs(in_l + left_size + 1, post_l + left_size, post_r - 1)
            print(left_size) #0 changed!!!
            return TreeNode(postorder[post_r - 1], left, right)

        return dfs(0, 0, len(postorder))  # 左闭右开区间


#lcs
class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        if not postorder:  # 空节点
            return None
        left_size = inorder.index(postorder[-1])  # 左子树的大小
        left = self.buildTree(inorder[:left_size], postorder[:left_size])
        right = self.buildTree(inorder[left_size + 1:], postorder[left_size: -1])
        return TreeNode(postorder[-1], left, right)




class Solution:
    def buildTree(self, inorder: list[int], postorder: list[int]) -> Optional[TreeNode]:
        if not inorder:
            return None
            
        # Root is the last element of postorder
        root = TreeNode(postorder[-1])
        stack = [root]
        
        # Pointer for inorder, starting from the end
        in_idx = len(inorder) - 1
        
        # Traverse postorder from second-to-last down to 0
        for i in range(len(postorder) - 2, -1, -1):
            curr_val = postorder[i]
            node = stack[-1]
            
            # If the top of the stack is NOT the current inorder root, 
            # the next node must be the right child.
            if node.val != inorder[in_idx]:
                node.right = TreeNode(curr_val)
                stack.append(node.right)
            else:
                # If it matches, we've finished the right subtree.
                # Pop the stack to find the parent node for the left child.
                while stack and stack[-1].val == inorder[in_idx]:
                    node = stack.pop()
                    in_idx -= 1
                
                # The next node in postorder is the left child of the last popped node.
                node.left = TreeNode(curr_val)
                stack.append(node.left)
                
        return root
```



<a id="lc-0102"></a>
#### 102. [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) [M]
`Tree` `Breadth-First Search` `Queue`
Description: Return the level order traversal of a binary tree.

##### Approach 1: BFS with deque
Idea: Use a queue to visit nodes level by level.

```python

class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if root is None:
            return []
        ans = []
        q = deque([root])
        while q:
            vals = []
            for _ in range(len(q)):
                node = q.popleft()
                vals.append(node.val)
                if node.left:  q.append(node.left)
                if node.right: q.append(node.right)
            ans.append(vals)
        return ans

class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        res = []
        def dfs(node, level):
            if not node:
                return
            if level == len(res):
                res.append([])
            res[level].append(node.val)
            dfs(node.left, level + 1)
            dfs(node.right, level + 1)
        dfs(root, 0)
        return res

# or if node: ...
# because if not node doesn't return anything

# problem XoX
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        res = []
        q = deque()
        q.append(root)
        while q:
            cur = []
            for _ in range(len(q)):
                node = q.popleft()
                if node:
                    cur.append(node.val)
                    q.append(node.left)
                    q.append(node.right)
            res.append(cur)
        return res[:-1]
        
```

<a id="lc-0103"></a>
#### 103. [Binary Tree Zigzag Level Order Traversal](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/) [M]
`Tree` `Breadth-First Search` `Queue`
Description: Return the zigzag level order traversal of a binary tree.

##### Approach 1: BFS with alternating direction
Idea: Use BFS, alternate the order of values at each level based on depth.

```python
class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if root is None:
            return []
        ans = []
        cur = [root]
        while cur:
            nxt = []
            vals = []
            for node in cur:
                vals.append(node.val)
                if node.left:  nxt.append(node.left)
                if node.right: nxt.append(node.right)
            cur = nxt
            ans.append(vals[::-1] if len(ans) % 2 else vals)
        return ans
```

<a id="lc-0107"></a>
#### 107. [Binary Tree Level Order Traversal II](https://leetcode.com/problems/binary-tree-level-order-traversal-ii/) [M]
`Tree` `Breadth-First Search` `Queue`
Description: Return the level order traversal of a binary tree in reverse order.

##### Approach 1: DFS
Idea: Use DFS to collect nodes level by level, then return reversed.

```python
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        res = []
        def dfs(node, lv):
            if node:
                if lv == len(res):
                    res.append([])
                res[lv].append(node.val)
                dfs(node.left, lv + 1)
                dfs(node.right, lv + 1)
        dfs(root, 0)
        return res
```

##### Approach 2: BFS with reversal
Idea: Standard BFS level-by-level, then reverse the result list.

```python
class Solution:
    def levelOrderBottom(self, root: Optional[TreeNode]) -> List[List[int]]:
        if not root:
            return []
        res = []
        q = deque([root])
        while q:
            cur = []
            for _ in range(len(q)):
                node = q.popleft()
                cur.append(node.val)
                if node.left: q.append(node.left)
                if node.right: q.append(node.right)
            res.append(cur)
        return res[::-1]
```



<a id="lc-0116"></a>
#### 116. [Populating Next Right Pointers in Each Node](https://leetcode.com/problems/populating-next-right-pointers-in-each-node/) [M]
`Tree` `Breadth-First Search` `Linked List` `Binary Tree`
Description: Fill the next pointer for each node to point to its right sibling.

##### Approach 1: DFS with level tracking
Idea: Use DFS to visit nodes level by level, connecting siblings via next pointers.

```python
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        pre = []
        def dfs(node, depth):
            if node:
                if depth == len(pre):
                    pre.append(node)
                else:
                    pre[depth].next = node
                    pre[depth] = node
                dfs(node.left, depth + 1)
                dfs(node.right, depth + 1)
        dfs(root, 0)
        return root

##### Approach 2: BFS with pairwise
Idea: Use BFS with pairwise() to connect adjacent nodes.

```python
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        if not root: return None
        q = [root]
        while q:
            for x, y in pairwise(q):
                x.next = y
            tmp = q
            q = []
            for node in tmp:
                if node.left: q.append(node.left)
                if node.right: q.append(node.right)            
        return root
```

##### Approach 3: Iterative with dummy node
Idea: Iterate through levels, using a dummy node to build next level's connections.

```python
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        cur = root
        while cur:
            nxt = dummy = Node()
            while cur:
                if cur.left:
                    nxt.next = cur.left
                    nxt = nxt.next
                if cur.right:
                    nxt.next = cur.right
                    nxt = nxt.next
                cur = cur.next
            cur = dummy.next
        return root
```

##### Approach 4: BFS with deque and dummy node
Idea: Use deque-based BFS with a dummy node to connect siblings.

```python
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        if not root: return None
        q = deque([root])
        while q:
            dum = cur = Node()
            for _ in range(len(q)):
                node = q.popleft()
                cur.next = node
                cur = cur.next
                if node.left: q.append(node.left)
                if node.right: q.append(node.right)
            cur.next = None
            dum.next = None
        return root
```


<a id="lc-0117"></a>
#### 117. [Populating Next Right Pointers in Each Node II](https://leetcode.com/problems/populating-next-right-pointers-in-each-node-ii/) [M]
`Tree` `Breadth-First Search` `Linked List`
Description: Connect each node to its immediate right neighbor when the binary tree is no longer perfect.

##### Approach 1: Level traversal using existing next pointers
Idea: Use a dummy node to build the next level while walking the current level through already connected `next` links.

```python
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        head = root
        while head:
            dummy = Node(0)
            curr = dummy
            node = head
            while node:
                if node.left:
                    curr.next = node.left
                    curr = curr.next
                if node.right:
                    curr.next = node.right
                    curr = curr.next
                node = node.next
            head = dummy.next
        return root
# Time: O(n), Space: O(1)
```

<a id="lc-0199"></a>
#### 199. [Binary Tree Right Side View](https://leetcode.com/problems/binary-tree-right-side-view/) [M]
`Tree` `Depth-First Search` `Breadth-First Search` `Queue`
Description: Return the rightmost node at each level of the tree.

##### Approach 1: BFS
Idea: Use BFS to visit nodes level by level, keeping only the last node at each level.

```python
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if not root: return []
        res = []
        q = deque([root])
        while q:
            lenth = len(q)
            for i in range(lenth):
                node = q.popleft()
                if i == lenth - 1:
                    res.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
        return res
```

##### Approach 2: DFS (right subtree first)
Idea: DFS, visiting right subtree first. Record node at each new depth.

```python
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        res = []
        def dfs(node, depth):
            if node is None:
                return
            if depth == len(res):
                res.append(node.val)
            dfs(node.right, depth + 1)
            dfs(node.left, depth + 1)
        dfs(root, 0)
        return res
```

##### Approach 3: Iterative DFS with stack
Idea: Use a stack to track nodes and depths, store rightmost value per depth.

```python
class Solution:
    def rightSideView(self, root: TreeNode) -> List[int]:
        res = dict()
        max_depth = -1

        stack = [(root, 0)]
        while stack:
            node, depth = stack.pop()

            if node is not None:
                max_depth = max(max_depth, depth)
                res.setdefault(depth, node.val)
                stack.append((node.left, depth + 1))
                stack.append((node.right, depth + 1))

        return [res[depth] for depth in range(max_depth + 1)]
```

##### Approach 4: BFS with dict
Idea: BFS with depth tracking in a dict, overwriting with each new rightmost value.

```python
class Solution:
    def rightSideView(self, root: TreeNode) -> List[int]:
        rightmost_value_at_depth = dict() # 深度为索引，存放节点的值
        max_depth = -1

        queue = deque([(root, 0)])
        while queue:
            node, depth = queue.popleft()

            if node is not None:
                max_depth = max(max_depth, depth)
                #popleft, append left first, right = last in level
                rightmost_value_at_depth[depth] = node.val
                queue.append((node.left, depth + 1))
                queue.append((node.right, depth + 1))

        return [rightmost_value_at_depth[depth] for depth in range(max_depth + 1)]
```

##### Approach 5: Iterative DFS with dict
Idea: Use DFS stack with depth tracking, only recording first encounter per depth (rightmost).

```python
class Solution:
    def rightSideView(self, root: TreeNode) -> List[int]:
        rightmost_value_at_depth = dict()
        max_depth = -1
        stack = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            if node is not None:
                max_depth = max(max_depth, depth)
                # set only if not exists
                rightmost_value_at_depth.setdefault(depth, node.val)
                stack.append((node.left, depth + 1))
                stack.append((node.right, depth + 1))
        return [rightmost_value_at_depth[depth] for depth in range(max_depth + 1)]
```

<a id="lc-0429"></a>
#### 429. [N-ary Tree Level Order Traversal](https://leetcode.com/problems/n-ary-tree-level-order-traversal/) [H]
`Tree` `Breadth-First Search` `Queue`
Description: Return the level order traversal of an N-ary tree.

##### Approach 1: BFS
Idea: Use a queue to traverse the tree level by level.

```python
class Solution:
    def levelOrder(self, root: 'Node') -> List[List[int]]:
        if root is None:
            return []
        ans = []
        q = [root]
        while q:
            ans.append([node.val for node in q])
            q = [c for node in q for c in node.children]
        return ans

class Solution:
    def levelOrder(self, root: 'Node') -> List[List[int]]:
        if root is None:
            return []
        ans = []
        q = deque([root])
        while q:
            vals = []
            for _ in range(len(q)):
                node = q.popleft()
                vals.append(node.val)
                q.extend(node.children)
            ans.append(vals)
        return ans
```





437. 路径总和 III (No solution)
```python
def pathSum(self, root: TreeNode, targetSum: int) -> int:
    def rootSum(root, targetSum):
        if root is None:
            return 0

        ret = 0
        if root.val == targetSum:
            ret += 1

        ret += rootSum(root.left, targetSum - root.val)
        ret += rootSum(root.right, targetSum - root.val)
        return ret
    
    if root is None:
        return 0
        
    ret = rootSum(root, targetSum)
    ret += self.pathSum(root.left, targetSum)
    ret += self.pathSum(root.right, targetSum)
    return ret

```

114. 二叉树展开为链表
```python


```


<a id="lc-lcr-413"></a>
#### LCR 413. [Substructure Determination](https://leetcode.cn/problems/HGSZAm/) [H]
`Tree` `Depth-First Search` `Binary Tree`
Description: Check if a binary tree B is a substructure of tree A.

##### Approach 1: DFS
Idea: Search for a match starting from each node in tree A, then verify structure match.

```python
class Solution:
    def isSubStructure(self, A: Optional[TreeNode], B: Optional[TreeNode]) -> bool:
        def dfs(A, B):
            if not B: return True
            if not A or A.val != B.val: return False
            return dfs(A.left, B.left) and dfs(A.right, B.right)
        return bool(A and B) and (dfs(A,B) or self.isSubStructure(A.left, B) or self.isSubStructure(A.right, B))
```

<a id="lc-0096"></a>
#### 96. [Unique Binary Search Trees](https://leetcode.com/problems/unique-binary-search-trees/) [H]
`Tree` `Dynamic Programming` `Binary Search Tree` `Math`
Description: Count the number of structurally unique BSTs with n nodes.

##### Approach 1: DP (Catalan number)
Idea: dp[i] = number of unique BSTs with i nodes = sum(dp[j] * dp[i-1-j]) for j=0..i-1.

```python
class Solution:
    def numTrees(self, n):
        """
        :type n: int
        :rtype: int
        """
        G = [0]*(n+1)
        G[0], G[1] = 1, 1

        for i in range(2, n+1):
            for j in range(1, i+1):
                G[i] += G[j-1] * G[i-j]

        return G[n]
```

##### Approach 2: Catalan formula
Idea: Use the mathematical formula for the nth Catalan number: C(2n, n) / (n+1).

```python
class Solution(object):
    def numTrees(self, n):
        """
        :type n: int
        :rtype: int
        """
        C = 1
        for i in range(0, n):
            C = C * 2*(2*i+1)/(i+2)
        return int(C)
```


314. 二叉树的垂直遍历
```python
```



---


### Hard
<a id="lc-0095"></a>
#### 95. [Unique Binary Search Trees II](https://leetcode.com/problems/unique-binary-search-trees-ii/) [H]
`Tree` `Backtracking` `Binary Search Tree` `Dynamic Programming`
Description: Generate all structurally unique BSTs with n nodes.

##### Approach 1: Recursive backtracking
Idea: For each value i as root, recursively generate all left and right subtrees, then combine.

```python
class Solution:
    def generateTrees(self, n: int) -> List[TreeNode]:
        def generateTrees(start, end):
            if start > end:
                return [None,]
            allTrees = []
            for i in range(start, end + 1):  # 枚举可行根节点
                leftTrees = generateTrees(start, i - 1)
                rightTrees = generateTrees(i + 1, end)
                for l in leftTrees:
                    for r in rightTrees:
                        currTree = TreeNode(i)
                        currTree.left = l
                        currTree.right = r
                        allTrees.append(currTree)
            return allTrees
        return generateTrees(1, n) if n else []
```

##### Approach 2: Memoized backtracking
Idea: Same as Approach 1, but use memoization to avoid recomputing subtrees.

```python
class Solution:
    def generateTrees(self, n: int) -> List[Optional[TreeNode]]:
        if n == 0: return []
        memo = {}
        def build(start, end):
            if start > end: return [None]
            if (start, end) in memo: return memo[(start, end)]
            res = []
            for i in range(start, end + 1):
                for l, r in product(build(start, i - 1), build(i + 1, end)):
                    res.append(TreeNode(i, l, r))
            memo[(start, end)] = res
            return res
        return build(1, n)
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
