# 563. 二叉树的坡度


def findTilt(self, root: TreeNode) -> int:   
    def dfs(root):
        nonlocal s
        if not root:
            return 0
        left = dfs(root.left)
        right = dfs(root.right)
        d = abs(left - right)
        s += d
        return left + right + root.val

    s = 0
    dfs(root)
    return s

































