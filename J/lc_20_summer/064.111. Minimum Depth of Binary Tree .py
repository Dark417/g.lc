"""
064.111. Minimum Depth of Binary Tree
二叉树的最小深度

Given a binary tree, find its minimum depth.

The minimum depth is the number of nodes along the shortest path 
from the root node down to the nearest leaf node.

Note: A leaf is a node with no children.

Example:

Given binary tree [3,9,20,null,null,15,7],

    3
   / \
  9  20
    /  \
   15   7
return its minimum depth = 2.



"""

# D
def minDepth(self, root: TreeNode) -> int:
    if not root: return 0
    if not root.left and not root.right: return 1
    if not root.left and root.right: 
        return self.minDepth(root.right) + 1
    if not root.right and root.left:
        return self.minDepth(root.left) + 1
    return min(self.minDepth(root.left), self.minDepth(root.right))+1


# official
# recursive dfs
def minDepth(self, root):
    if not root:
        return 0

    children = [root.left, root.right]
    # if we're at leaf node
    if not any(children):
        return 1

    min_depth = float('inf')
    for c in children:	# only watch non-Nones!
        if c:
            min_depth = min(self.minDepth(c), min_depth)
    return min_depth + 1
    # when None, depth = 1



# iterative dfs
def minDepth(self, root):
    if not root:
        return 0
    else:
        stack, min_depth = [(1, root),], float('inf')

    while stack:
        depth, root = stack.pop()
        children = [root.left, root.right]
        if not any(children):
            min_depth = min(depth, min_depth)
        for c in children:
            if c:
                stack.append((depth + 1, c))
    return min_depth

# bfs
from collections import deque
class Solution:
    def minDepth(self, root):
        if not root:
            return 0
        else:
            node_deque = deque([(1, root),])
        while node_deque:
            depth, root = node_deque.popleft()
            children = [root.left, root.right]
            if not any(children):
                return depth
            for c in children:
                if c:
                    node_deque.append((depth + 1, c))


# Stefan
def minDepth(self, root):
    if not root: return 0
    d = map(self.minDepth, (root.left, root.right))
    return 1 + (min(d) or max(d))

def minDepth(self, root):
    if not root: return 0
    d, D = sorted(map(self.minDepth, (root.left, root.right)))
    return 1 + (d or D)



# bfs
def minDepth(self, root):
    if root==None:
        return 0
    stack=[(root,1)]
    while len(stack)!=0:
        node=stack.pop(0)
        if node[0]==None:
            continue
            # ignore none, for c in children...
        if node[0].left==None and node[0].right==None:
        	# leave detected
            return node[1]
        else:
            stack.append((node[0].left,node[1]+1))
            stack.append((node[0].right,node[1]+1))
    return 0

# BFS   
def minDepth(self, root):
    if not root:
        return 0
    queue = collections.deque([(root, 1)])
    while queue:
        node, level = queue.popleft()
        if node:
            if not node.left and not node.right:
                return level
            else:
                queue.append((node.left, level+1))
                queue.append((node.right, level+1))



# DFS
def minDepth1(self, root):
    if not root:
        return 0
    if None in [root.left, root.right]:
    	# same
    	# return self.minDepth(root.left)+self.minDepth(root.right)+1
        return max(self.minDepth(root.left), self.minDepth(root.right)) + 1
    else:
        return min(self.minDepth(root.left), self.minDepth(root.right)) + 1
 
def minDepth(self, root):
    if not root: 
        return 0;
    left = self.minDepth(root.left);
    right = self.minDepth(root.right);
    if left == 0 or right == 0:
        return left + right + 1
    return min(left, right) + 1


def minDepth(self, root: TreeNode) -> int:
    if not root : return 0
	    leftDepth = self.minDepth(root.left)
	    rightDepth = self.minDepth(root.right)
	    childDepth = min(leftDepth, rightDepth) if leftDepth and rightDepth else leftDepth or rightDepth
    return 1 + childDepth


def minDepth(self, root):
    depth, level = 0, [root]
    while level and level[0]:
        depth += 1
        NotLast = (None,None) not in [(n.left, n.right) for n in level ]
        level = NotLast and [k for n in level for k in (n.left,n.right) if k]
    return depth


def minDepth(self, R: TreeNode) -> int:
    if not R: return 0
    N, A, d = [R], [], 1
    while 1:
        for n in N:
            if n.left is n.right: return d
            n.left and A.append(n.left), n.right and A.append(n.right)
        N, A, d = A, [], d + 1































