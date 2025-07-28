# 面试题 17.12. BiNode

def convertBiNode(self, root):
    self.pre = self.ans = TreeNode(-1)
    def dfs(root):
        if not root: return
        dfs(root.left)
        root.left = None
        self.pre.right = root
        self.pre = root
        dfs(root.right)
    dfs(root)
    return self.ans.right




