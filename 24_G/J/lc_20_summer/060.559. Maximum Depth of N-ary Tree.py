"""
060.559. Maximum Depth of N-ary Tree
N叉树的最大深度


Given a n-ary tree, find its maximum depth.

The maximum depth is the number of nodes along the longest path 
from the root node down to the farthest leaf node.

Nary-Tree input serialization is represented in their level order traversal, 
each group of children is separated by the null value (See examples).

 

Example 1:



Input: root = [1,null,3,2,4,null,5,6]
Output: 3
Example 2:



Input: root = [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
Output: 5
 

Constraints:

The depth of the n-ary tree is less than or equal to 1000.
The total number of nodes is between [0, 10^4].



"""

# official
# recursion
def maxDepth(self, root):
    if root is None: 
        return 0 
    else: 
        left_height = self.maxDepth(root.left) 
        right_height = self.maxDepth(root.right) 
        return max(left_height, right_height) + 1 


# iteration
def maxDepth(self, root):
    stack = []
    if root is not None:
        stack.append((1, root))
    depth = 0
    while stack != []:
        current_depth, root = stack.pop()
        if root is not None:
            depth = max(depth, current_depth)
            stack.append((current_depth + 1, root.left))
            stack.append((current_depth + 1, root.right))
    return depth


def maxDepth(self, root: TreeNode) -> int:
    def bottom_up(node):
        return 0 if node is None else max(bottom_up(node.left), bottom_up(node.right)) + 1
    return bottom_up(root)


def maxDepth(self, root: TreeNode) -> int:
    def top_down(node, h):
        return h if node is None else max(top_down(node.left, h + 1), top_down(node.right, h + 1))
    return top_down(root, 0)



def maxDepth(self, root):
    return 1 + max(map(self.maxDepth, (root.left, root.right))) if root else 0
    return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right)) if root else 0

    return root and 1 + max(map(self.maxDepth, (root.left, root.right))) or 0


# bfs
def maxDepth(self, root):
    q = deque()
    if not root:
        return 0
    q.append(root)	#queue = [root]
    maxdepth = 0
    while q:
        maxdepth += 1
        level_len = len(q)        
        for _ in range(level_len):
            node = q.popleft()	#queue.pop(0)
            if node.left:	#if node.left is not None:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return maxdepth


def maxDepth(self, root):
    depth = 0
    level = [root] if root else []
    while level:
        depth += 1
        queue = []
        for el in level:
            if el.left:
                queue.append(el.left)
            if el.right:
                queue.append(el.right)
        level = queue
    return depth


# bfs m0
def maxDepth(self, root: TreeNode) -> int:
    q = deque([root])
    level = 0
    while q:
        n = len(q)
        for i in range(n):
            node = q.popleft()
            if node:  # is not None
                q.extend([node.left, node.right])
        level += 1
    return level - 1


# bfs m1
def maxDepth(self, root: TreeNode) -> int:
    if root:
        level = [root] # 当前层所有node
        depth = 0
        while level:
            new_level = []
            for node in level:
                if node:
                    new_level.extend([node.left, node.right])
            level = new_level	# replace, one additional variable
            depth += 1
        return depth-1
    return 0


def maxDepth(self, root):     
     if not root:
         return 0
     tstack,h = [root],0
     #count number of levels
     while tstack:
         nextlevel = []
         while tstack:
             top = tstack.pop()
             if top.left:
                 nextlevel.append(top.left)
             if top.right:
                 nextlevel.append(top.right)
         tstack = nextlevel
         h+=1
     return h


def maxDepth(self, root: TreeNode) -> int:
    if not root:
        return 0
    worklist = deque([root])
    num_node_level = 1
    levels = 0
    while worklist:
        node = worklist.popleft()
        if node.left:
            worklist.append(node.left)
        if node.right:
            worklist.append(node.right)
        num_node_level -= 1
        if num_node_level == 0:
            levels += 1
            num_node_level = len(worklist)
    return levels


# BFS + deque   
def maxDepth(self, root):
    if not root:
        return 0
    from collections import deque
    queue = deque([(root, 1)])
    while queue:
        curr, val = queue.popleft()
        if not curr.left and not curr.right and not queue:
            return val
        if curr.left:
            queue.append((curr.left, val+1))
        if curr.right:
            queue.append((curr.right, val+1))

 
# DFS    
def maxDepth(self, root):
    res = 0
    stack = [(root, 0)]
    while stack:
        node, level = stack.pop()
        if not node:
            res = max(res, level)
        else:
            stack.append((node.right, level+1))
            stack.append((node.left, level+1))
    return res



# tuple, max

# top down
def maxDepth(self, root):
    # use BFS with iterative 
    # BFS + deque   
    if not root:
        return 0
    queue = collections.deque([(root, 1)]) # here the 2nd number is level
    while queue:
        curr, val = queue.popleft()
        if curr.left:
            queue.append((curr.left, val+1))
        if curr.right:
            queue.append((curr.right, val+1))
    return val
    # not critical, unintentionally count left


# update max at leaves
# def maxDepth(self, root):
#     if not root: return 0
#     max_depth = 0   
#     counter = 1
#     stack = [(root,counter)]
#     while stack:
#         node,depth = stack.pop()
#         if node.left:
#             stack.append((node.left,depth+1))
#         if node.right:
#             stack.append((node.right,depth+1))
#         if not node.left and not node.right :
#             max_depth = max(max_depth,depth)
#     return max_depth









### multi 
def maxDepth(self, root):
    if not root: return 0
    if not root.children: return 1
    return max(self.maxDepth(node) for node in root.children) + 1

    return max((self.maxDepth(child) for child in root.children), default=0) + 1 if root else 0

    # base?
    if(len(root.children)==0): return 1


#dfs
def maxDepth(self, root):
    if not root:
        return 0
    return max(self.maxDepth(root.left),self.maxDepth(root.right)) + 1

    return max(root and [self.maxDepth(child, level + 1) for child in root.children] + [level] or [0])

    return 1 + max([self.maxDepth(n) for n in root.children] + [0]) if root else 0 



# map
def maxDepth(self, root):
    if not root: return 0
    return 1 + max(map(self.maxDepth, root.children or [None]))

# bfs
def maxDepth(self, root):
    queue = []
    if root: queue.append((root, 1))
    depth = 0
    for (node, level) in queue:
        depth = level
        queue += [(child, level+1) for child in node.children]
    return depth


    if root == None: return 0
	q = queue.Queue()  
	level = 1
	q.put((root, level))
	depth = 0
	while not q.empty():
	    curr_node, level = q.get()
	    depth = level
	    for child in curr_node.children:
	        q.put((child, level+1))
	return depth


def maxDepth(self, root):
    q, level = root and [root], 0
    while q:
        q, level = [child for node in q for child in node.children if child], level + 1
    return level 


def maxDepth(self, root):
        if root == None:
            return 0
        depth = 0
        stack = [root]
        while stack:
            next_level = []
            while stack:
                node = stack.pop()
                if node.children:
                    next_level += node.children
            stack = next_level
            depth += 1
        return depth

# dfs stack
def maxDepth(self, root):
    stack = []
    if root: stack.append((root, 1))
    depth = 0
    while stack:
        (node, d) = stack.pop()
        depth = max(depth, d)
        for child in node.children:
            stack.append((child, d+1))
    return depth


# recursion
def maxDepth(self, root):
    if root is None:
        return 0
    return self.maxDepthHelper(root, 1, 1)

def maxDepthHelper(self, root, depth, maxDepth):
    if root is None:
        return maxDepth
    maxDepth = max(depth, maxDepth)
    for child in root.children:
        maxDepth = self.maxDepthHelper(child, depth + 1, maxDepth)
    return maxDepth



# not too much
class Solution1(object):
    def maxDepth(self, root):
        if not root: return 0 #base case 1
        if not root.children: return 1 #base case 2
        heights = [] #hold all the heights of root's children 
        for node in root.children:
            heights.append(self.maxDepth(node))

        height = [self.maxDepth(node) for node in root.children]
        return max(heights) + 1

        return max(self.maxDepth(node) for node in root.children) + 1   

#Compare the heights in a loop
class Solution4(object):
    def maxDepth(self, root):
        if not root: return 0
        height = 0
        for node in root.children:
            height = max(self.maxDepth(node), height)
        return height + 1


















