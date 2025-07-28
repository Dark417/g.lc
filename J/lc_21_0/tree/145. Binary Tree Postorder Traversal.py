"""
145. Binary Tree Postorder Traversal
二叉树的后序遍历

Given the root of a binary tree, return the postorder traversal of its nodes' values.

 

Example 1:


Input: root = [1,null,2,3]
Output: [3,2,1]
Example 2:

Input: root = []
Output: []
Example 3:

Input: root = [1]
Output: [1]
Example 4:


Input: root = [1,2]
Output: [2,1]
Example 5:


Input: root = [1,null,2]
Output: [2,1]
 

Constraints:

The number of the nodes in the tree is in the range [0, 100].
-100 <= Node.val <= 100

"""




def postorderTraversal(self, root: TreeNode) -> List[int]:
    def dfs(node):
        if node:
            dfs(node.left)
            dfs(node.right)
            res.append(node.val)
    res = []
    dfs(root)
    return res



# reverse preorder
def postorderTraversal(self, root):
    traversal, stack = [], [root]
    while stack:
        node = stack.pop()
        if node:
            # pre-order, right first
            traversal.append(node.val)
            stack.append(node.left)
            stack.append(node.right)

    # reverse result
    return traversal[::-1]



def postorderTraversal(self, root: TreeNode) -> List[int]:
	if not root: return []
	cur, stack, res, = root, [], []
	while cur or stack:
		while cur:
			res.append(cur.val)
			stack.append(cur)
			cur = cur.right
		tmp = stack.pop()
		cur = tmp.left
	return res[::-1]




def postorderTraversal(self, root):
    stack, res = [], []
    while stack or root:
        if root:
            stack.append(root)
            res.append(root.val)    
            root = root.right     #先加右边，在左边。
        else:
            node = stack.pop()
            root = node.left
    return res[::-1]     #返回Reversed的list




def postorderTraversal(self, root):
    traversal, stack = [], [(root, False)]
    while stack:
        node, visited = stack.pop()
        if node:
            if visited:
                # add to result if visited
                traversal.append(node.val)
            else:
                # post-order
                stack.append((node, True))
                stack.append((node.right, False))
                stack.append((node.left, False))

    return traversal







def postorderTraversal(self, root):
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
            stack.append(root.val)					# 后序遍历
            stack.append(root.right) 
            stack.append(root.left)
    return out




































