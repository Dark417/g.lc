"""
065.513. Find Bottom Left Tree Value
找树左下角的值


Given a binary tree, find the leftmost value in the last row of the tree.

Example 1:
Input:

    2
   / \
  1   3

Output:
1
Example 2:
Input:

        1
       / \
      2   3
     /   / \
    4   5   6
       /
      7

Output:
7
Note: You may assume the tree (i.e., the given root node) is not NULL.



"""
def findBottomLeftValue(self, root: TreeNode) -> int:
	queue = [root]
    while queue:
        node = queue.pop(0)
        res = node.val
        if node.right:
            queue.append(node.right)
        if node.left:
            queue.append(node.left)
    return res


# Stefan
def findLeftMostNode(self, root):
    queue = [root]
    for node in queue:
        queue += filter(None, (node.right, node.left))
    return node.val






#BFS + queue
def findBottomLeftValue(self, root):
    if not root:
        return
    max_depth = 0
    queue = [(root, 1)]
    
    while queue:
        curr, level = queue.pop(0)
        if curr:
            if level > max_depth:
                max_depth = level
                ans = curr.val
            queue.append((curr.left, level + 1))
            queue.append((curr.right, level + 1))
    return ans


#DFS + stack   
def findBottomLeftValue(self, root):
    if not root:
        return
    max_depth = 0
    stack = [(root, 1)]
     
    while stack:
        curr, level = stack.pop()
        if curr:
            if level > max_depth:
                max_depth = level
                ans = curr.val
            stack.append((curr.right, level + 1))
            stack.append((curr.left, level + 1))
    return ans


def get_node(self, root, curr_height=1): 
    if not root:
        return [-1, -1]
    if not root.left and not root.right:
        return [root.val, curr_height]
    left = self.get_node(root.left, curr_height + 1)
    right = self.get_node(root.right, curr_height + 1)
    return left if left[1] >= right[1] else right
    
def findBottomLeftValue(self, root: TreeNode) -> int:
    return self.get_node(root)[0]



def findBottomLeftValue(self, root):
    queue=[root]; #ans=0
    while any(queue): 		#while row:
        ans=queue[0].val
        queue=[leaf for node in queue for leaf in (node.left,node.right) if leaf]
    return ans


def findBottomLeftValue(self, root):
    row = [root]
    while row:
        first = row[0].val
        row = [child for node in row for child in (node.left, node.right) if child]
    return first





def findBottomLeftValue(self, root: TreeNode) -> int:
    def dfs(root, depth):
        if not root: return
        if depth > self.maxdepth:
            self.maxdepth = depth
            self.res = root.val    
        dfs(root.left, depth+1)
        dfs(root.right, depth+1)
    self.maxdepth, self.res = -1, 0
    dfs(root, 0)
    return self.res


def findBottomLeftValue(self, root: TreeNode) -> int:
    def dfs(root):
        if not root: return None, 0
        if not root.left and not root.right:
            return root.val, 1 
        left_val, left_depth = dfs(root.left)
        right_val, right_depth = dfs(root.right)
        if left_depth >= right_depth:
            return left_val, 1 +left_depth
        return right_val, 1 + right_depth

    return dfs(root)[0]




def findBottomLeftValue(self, root: TreeNode) -> int:
    if not root: return []
    cur, res = [root], None
    while cur:
        layer, res = [], cur[0].val
        for node in cur:
            if node.left: layer.append(node.left)
            if node.right: layer.append(node.right)
        cur = layer
    return res






def findBottomLeftValue(self, root):
    q = collections.deque()
    res = None
    q.appendleft(root)
    
    while q:
        sz = len(q)
        for i in xrange(0, sz):
            node = q.popleft()
            if i == 0:
                res = node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return res



























]