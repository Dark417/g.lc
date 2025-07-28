# 235. 二叉搜索树的最近公共祖先


def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
    while (root.val - p.val) * (root.val - q.val) > 0:
        if root.val > q.val:
            root = root.left
        else:
            root = root.right
    return root


def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
    if (root.val - q.val) * (root.val - p.val) <= 0:
        return root
    
    return self.lowestCommonAncestor(root.left, p, q) if p.val < root.val else self.lowestCommonAncestor(root.right, p, q)


def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    ancestor = root
    while True:
        if p.val < ancestor.val and q.val < ancestor.val:
            ancestor = ancestor.left
        elif p.val > ancestor.val and q.val > ancestor.val:
            ancestor = ancestor.right
        else:
            break
    return ancestor


def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
	if root.val < p.val and root.val < q.val:
		return self.lowestCommonAncestor(root.right, p, q)
	if root.val > p.val and root.val > q.val:
		return self.lowestCommonAncestor(root.left, p, q)
	return root


def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
    def dfs(root, p, q):
        if root is None:
            return 0
        val = 0
        if root.val == p.val:
            val = 1
        if root.val == q.val:
            val = 2
        val += dfs(root.left, p, q) + dfs(root.right, p, q) 
        if val == 3:
            self.res = root
            return 0
        else:
            return val
    self.res = None
    dfs(root, p, q)
    return self.res





















