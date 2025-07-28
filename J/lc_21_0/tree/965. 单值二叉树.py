# 965. 单值二叉树

def isUnivalTree(self, root: TreeNode) -> bool:
    left = (not root.left or root.val == root.left.val and self.isUnivalTree(root.left))
    right = (not root.right or root.val == root.right.val and self.isUnivalTree(root.right))
    return left and right



def isUnivalTree(self, root: TreeNode) -> bool:
    def dfs(node, v):
        if not node:
            return True
        if node.val == v:
            return dfs(node.left, v) and dfs(node.right, v)
        else:
            return False
    return dfs(root, root.val)

























