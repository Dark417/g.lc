"""
94. Binary Tree Inorder Traversal
二叉树中序遍历

"""

# recursively
def inorderTraversal1(self, root):
    res = []
    self.helper(root, res)
    return res
    
def helper(self, root, res):
    if root:
        self.helper(root.left, res)
        res.append(root.val)
        self.helper(root.right, res)


# iteratively       
# def inorderTraversal(self, root):
#     res, stack = [], []
#     while True:
#         while root:
#             stack.append(root)
#             root = root.left
		# exit
        if not stack:
            return res
        # node = stack.pop()
        # res.append(node.val)
        # root = node.right


def inorderTraversal(self, root: TreeNode) -> List[int]:
	if not root: return []
	cur, stack, res, = root, [], []
	while cur or stack:
		while cur:
			stack.append(cur)
			cur = cur.left	
			
		cur = stack.pop()
		res.append(cur.val)
		cur = cur.right
	return res



def inorderTraversal(self, root):
    result, stack = [], [(root, False)]

    while stack:
        cur, visited = stack.pop()
        if cur:
            if visited:
                result.append(cur.val)
            else:
                stack.append((cur.right, False))
                stack.append((cur, True))
                stack.append((cur.left, False))

    return result






def inorderTraversal(self, root):
    if root is None:
        return []
    t = type(root)
    out = []
    stack = [root]
    while stack:
        root = stack.pop()
        if type(root) != t and root is not None:
            out.append(root)
            continue
        if root:    
            stack.append(root.right)
            stack.append(root.val)					# 中序遍历
            stack.append(root.left)
    return out













def Morris(root): 
	# Set current to root of binary tree 
	curr = root 
	
	while(curr is not None): 
		
		if curr.left_node is None: 
			print curr.data, 
			curr = curr.right_node 
		else: 
			# Find the previous (prev) of curr 
			prev = curr.left_node 
			while(prev.right_node is not None and prev.right_node != curr): 
				prev = prev.right_node 

			# Make curr as right child of its prev 
			if(prev.right_node is None): 
				prev.right_node = curr 
				curr = curr.left_node 
				
			# fix the right child of prev
			else: 
				prev.right_node = None
				print curr.data, 
				curr = curr.right_node




def morris_traversal(root): 
    """Generator function for iterative inorder tree traversal"""
  
    current = root 
      
    while current is not None: 
          
        if current.left is None: 
            yield current.data 
            current = current.right 
        else: 
  
            # Find the inorder predecessor of current 
            pre = current.left 
            while pre.right is not None and pre.right is not current: 
                pre = pre.right 
  
            if pre.right is None: 
  
                # Make current as right child of its inorder predecessor 
                pre.right = current 
                current = current.left         
  
            else: 
                # Revert the changes made in the 'if' part to restore the  
                # original tree. i.e., fix the right child of predecessor 
                pre.right = None
                yield current.data 
                current = current.right































