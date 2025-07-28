#104. 二叉树的最大深度

def maxDepth(self, root: TreeNode) -> int:
    def dfs(node):
        if node:
            left = dfs(node.left)
            right = dfs(node.right)
            self.m = max(self.m, max(left, right) + 1)
            return max(left, right) + 1
        else:
            return 0
    self.m = 0
    dfs(root)
    return self.m






























