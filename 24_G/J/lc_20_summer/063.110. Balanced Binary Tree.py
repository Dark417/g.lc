"""
063.110. Balanced Binary Tree


Given a binary tree, determine if it is height-balanced.

For this problem, a height-balanced binary tree is defined as:

a binary tree in which the left and right subtrees of every node differ in height by no more than 1.



Example 1:

Given the following tree [3,9,20,null,null,15,7]:

    3
   / \
  9  20
    /  \
   15   7
Return true.

Example 2:

Given the following tree [1,2,2,3,3,null,null,4,4]:

       1
      / \
     2   2
    / \
   3   3
  / \
 4   4
Return false.

"""



# top down
def height(self, root):
    if not root: return -1
    return max(self.height(root.left), self.height(root.right)) + 1

def isBalanced(self, root: TreeNode) -> bool:
    if not root: return True
    return abs(self.height(root.left) - self.height(root.right)) <= 1 
    and self.isBalanced(root.left) and self.isBalanced(root.right)


# official
# bottom up
# Return whether or not the tree at root is balanced while also returning
# the tree's height
def isBalancedHelper(self, root: TreeNode) -> (bool, int):
    # An empty tree is balanced and has height -1
    if not root:
        return True, -1
    
    # Check subtrees to see if they are balanced. 
    leftIsBalanced, leftHeight = self.isBalancedHelper(root.left)
    if not leftIsBalanced:
        return False, 0
    rightIsBalanced, rightHeight = self.isBalancedHelper(root.right)
    if not rightIsBalanced:
        return False, 0
    
    # If the subtrees are balanced, check if the current tree is balanced
    # using their height
    return (abs(leftHeight - rightHeight) < 2), 1 + max(leftHeight, rightHeight)
    
def isBalanced(self, root: TreeNode) -> bool:
    return self.isBalancedHelper(root)[0]


# bottom up
def recur(self, root):
    if not root: return 0
    left = self.recur(root.left)
    if left == -1: return -1
    right = self.recur(root.right)
    if right == -1: return -1
    return max(left, right) + 1 if abs(left - right) < 2 else -1

def isBalanced(self, root: TreeNode) -> bool:
    return self.recur(root) != -1


# postorder traversal:
def isBalanced(self, root):
    stack, node, last, depths = [], root, None, {}
    # depths = collections.defaultdict(int)
    while stack or node:
        if node:
            stack.append(node)
            node = node.left
        else:
            node = stack[-1]
            if not node.right or last == node.right:
                node = stack.pop()
                left, right  = depths.get(node.left, 0), depths.get(node.right, 0)
                if abs(left - right) > 1: return False
                depths[node] = 1 + max(left, right)
                last = node
                node = None
            else:
                node = node.right
    return True


#
def isBalanced(self, root):
    stack = [(0, root)]
    depth = {None: 0}
    while stack:
        seen, node = stack.pop()
        if node is None:
            continue
        if not seen:
            stack.extend([(1, node), (0, node.right), (0, node.left)])
        else:
            if abs(depth[node.left] - depth[node.right]) > 1:
                return False
            depth[node] = max(depth[node.left], depth[node.right]) + 1
    return True



# 2 in 1
def check(node):
    if node == None:
        return (0, True)
    l_depth, l_balanced = check(node.left)
    r_depth, r_balanced = check(node.right)
    return max(l_depth, r_depth) + 1, l_balanced and r_balanced and abs(l_depth - r_depth) <= 1

class Solution:
    def isBalanced(self, root):
        return check(root)[1]


#
def isBalanced(self, root):
    if not root:
        return True
    max_, min_ = self.calMaxMin(root)
    return max_ - min_ <= 1
    
def calMaxMin(self,root):
    if not root:
        return 0, 0
    else:
        tmp_left = self.calMaxMin(root.left)
        tmp_right = self.calMaxMin(root.right)
        _max = max(tmp_left[0], tmp_right[0]) + 1
        _min = min(tmp_left[1], tmp_right[1]) + 1
        return _max, _min












































