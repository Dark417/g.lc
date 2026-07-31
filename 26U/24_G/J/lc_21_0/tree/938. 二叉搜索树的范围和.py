# 938. 二叉搜索树的范围和


def rangeSumBST(self, root, L, R):
    def dfs(node):
        if node:
            if L <= node.val <= R:
                self.ans += node.val
            if L < node.val:
                dfs(node.left)
            if node.val < R:
                dfs(node.right)

    self.ans = 0
    dfs(root)
    return self.ans



# 多余
def rangeSumBST(self, root: TreeNode, low: int, high: int) -> int:
    def dfs(root, low, high):
        nonlocal s
        if root:
            if root.val >= low and root.val <= high:
                s += root.val
            dfs(root.left, low, high)
            dfs(root.right, low, high)
        
    s = 0
    dfs(root, low, high)
    return s
























