"""
117.112. Path Sum

路径总和

Given a binary tree and a sum, determine if the tree has a root-to-leaf path such 
that adding up all the values along the path equals the given sum.

Note: A leaf is a node with no children.

Example:

Given the below binary tree and sum = 22,

      5
     / \
    4   8
   /   / \
  11  13  4
 /  \      \
7    2      1
return true, as there exist a root-to-leaf path 5->4->11->2 which sum is 22.



"""

def hasPathSum(self, root: TreeNode, sum: int) -> bool:
    if not root: return False
    cur = [(root, sum)]
    while cur:
        node = cur.pop(0)
        curv = node[1] - node[0].val
        if not node[0].left and not node[0].right and curv == 0:
            return True
        else:
            if node[0].left: cur.append((node[0].left, curv))
            if node[0].right: cur.append((node[0].right, curv))
    return False



def hasPathSum(self, root: TreeNode, sum: int) -> bool:
    from collections import deque
    if not root: return False
    cur = deque()
    cur.append((root, sum))
    while cur:
        node = cur.popleft()
        curv = node[1] - node[0].val
        if not node[0].left and not node[0].right and curv == 0:
            return True
        else:
            if node[0].left: cur.append((node[0].left, curv))
            if node[0].right: cur.append((node[0].right, curv))
    return False


# recursion
def hasPathSum(self, root: TreeNode, sum: int) -> bool:
    def rec(node, curv):
        if not node: return False
        else:
            curv = curv - node.val
            if not node.left and not node.right and curv == 0:
                return True
            else:
                return rec(node.left, curv) or rec(node.right, curv)
    return rec(root, sum)


# recursion
def hasPathSum(self, root, sum):
    if not root: return False
    if not root.left and not root.right:
        return sum == root.val
    return self.hasPathSum(root.left, sum - root.val) or self.hasPathSum(root.right, sum - root.val)


# backtracking
def hasPathSum(self, root, sum):
    if not root: return False
    res = []
    return self.dfs(root, sum, res, [root.val])
    
def dfs(self, root, target, res, path):
    if not root: return False
    if sum(path) == target and not root.left and not root.right:
        return True
    left_flag, right_flag = False, False
    if root.left:
        left_flag = self.dfs(root.left, target, res, path + [root.left.val])
    if root.right:
        right_flag = self.dfs(root.right, target, res, path + [root.right.val])
    return left_flag or right_flag


# bfs
def hasPathSum(self, root: TreeNode, sum: int) -> bool:
    if not root:
        return False
    que = collections.deque()
    que.append((root, root.val))
    while que:
        node, path = que.popleft()
        if not node.left and not node.right and path == sum:
            return True
        if node.left:
            que.append((node.left, path + node.left.val))
        if node.right:
            que.append((node.right, path + node.right.val))
    return False


def hasPathSum(self, root, sum):
    if not root:
        return False
    stack = []
    stack.append((root, root.val))
    while stack:
        node, path = stack.pop()
        if not node.left and not node.right and path == sum:
            return True
        if node.left:
            stack.append((node.left, path + node.left.val))
        if node.right:
            stack.append((node.right, path + node.right.val))
    return False


































