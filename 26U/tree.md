# Tree

## Category

### Medium
- [M] [236. Lowest Common Ancestor of a Binary Tree](#lc-0236) — Find the lowest common ancestor of two nodes in a binary tree.
  `Tree` `Depth-First Search` `Binary Tree`

### Hard
- [H] [124. Binary Tree Maximum Path Sum](#lc-0124) — Find the maximum path sum in a binary tree.
  `Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
- [H] [297. Serialize and Deserialize Binary Tree](#lc-0297) — Design an algorithm to serialize and deserialize a binary tree.
  `Tree` `Depth-First Search` `Breadth-First Search` `Design`
- [H] [968. Binary Tree Cameras](#lc-0968) — Minimum cameras to monitor all nodes.
  `Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
- [H] [987. Vertical Order Traversal of a Binary Tree](#lc-0987) — Return the vertical order traversal of a binary tree.
  `Tree` `Depth-First Search` `Breadth-First Search` `Hash Table`
- [H] [1028. Recover a Tree From Preorder Traversal](#lc-1028) — Recover a binary tree from its preorder traversal string.
- [H] [1483. Kth Ancestor of a Tree Node](#lc-1483) — Find the kth ancestor of a given node.
  `Bit Manipulation` `Tree` `Depth-First Search` `Breadth-First Search`
- [H] [2603. Collect Coins in a Tree](#lc-2603) — Minimum edges to traverse to collect all coins and return.
  `Tree` `Graph` `Topological Sort` `Array`
- [H] [2791. Count Paths That Can Form a Palindrome in a Tree](#lc-2791) — Count paths whose character sequence can form a palindrome.
  `Bit Manipulation` `Tree` `Depth-First Search` `Dynamic Programming`
- [H] [2872. Maximum Number of K-Divisible Components](#lc-2872) — Maximum components where each has sum divisible by k.
  `Tree` `Depth-First Search`
- [H] [3562. Maximum Profit from Trading Stocks with Discounts](#lc-3562) — Maximum profit trading stocks on a tree with discounts.
  `Tree` `Depth-First Search` `Array` `Dynamic Programming`
- [H] [LCR 051. 二叉树中的最大路径和](#lc-lcr-051) — 求二叉树中的最大路径和.
  `Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`

## Solutions (Python)

<a id="lc-0124"></a>
#### 124. [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) [H]
`Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
Description: Find the maximum path sum in a binary tree where any node can be the start or end.

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

<a id="lc-0968"></a>
#### 968. [Binary Tree Cameras](https://leetcode.com/problems/binary-tree-cameras/) [H]
`Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
Description: Find the minimum number of cameras needed to monitor all nodes in a binary tree.

<a id="lc-0987"></a>
#### 987. [Vertical Order Traversal of a Binary Tree](https://leetcode.com/problems/vertical-order-traversal-of-a-binary-tree/) [H]
`Tree` `Depth-First Search` `Breadth-First Search` `Hash Table`
Description: Return the vertical order traversal of a binary tree's values.

<a id="lc-1028"></a>
#### 1028. [Recover a Tree From Preorder Traversal](https://leetcode.com/problems/recover-a-tree-from-preorder-traversal/) [H]
Description: Recover a binary tree from a string representation of its preorder traversal with dashes.

<a id="lc-1483"></a>
#### 1483. [Kth Ancestor of a Tree Node](https://leetcode.com/problems/kth-ancestor-of-a-tree-node/) [H]
`Bit Manipulation` `Tree` `Depth-First Search` `Breadth-First Search`
Description: Find the kth ancestor of a given node in a tree.

<a id="lc-2603"></a>
#### 2603. [Collect Coins in a Tree](https://leetcode.com/problems/collect-coins-in-a-tree/) [H]
`Tree` `Graph` `Topological Sort` `Array`
Description: Find the minimum number of edges to traverse to collect all coins and return to start.

<a id="lc-2791"></a>
#### 2791. [Count Paths That Can Form a Palindrome in a Tree](https://leetcode.com/problems/count-paths-that-can-form-a-palindrome-in-a-tree/) [H]
`Bit Manipulation` `Tree` `Depth-First Search` `Dynamic Programming`
Description: Count paths in a tree whose character labels can be rearranged to form a palindrome.

<a id="lc-2872"></a>
#### 2872. [Maximum Number of K-Divisible Components](https://leetcode.com/problems/maximum-number-of-k-divisible-components/) [H]
`Tree` `Depth-First Search`
Description: Split a tree into the maximum number of components where each has sum divisible by k.

<a id="lc-3562"></a>
#### 3562. [Maximum Profit from Trading Stocks with Discounts](https://leetcode.com/problems/maximum-profit-from-trading-stocks-with-discounts/) [H]
`Tree` `Depth-First Search` `Array` `Dynamic Programming`
Description: Maximize profit from trading stocks on a tree structure with parent-child discounts.

<a id="lc-lcr-051"></a>
#### LCR 051. [二叉树中的最大路径和](https://leetcode.cn/problems/jC7MId/) [H]
`Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
Description: 求二叉树中的最大路径和（同 124 题）。
