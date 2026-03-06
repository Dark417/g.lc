# 700. 二叉搜索树中的搜索

def searchBST(self, root: TreeNode, val: int) -> TreeNode:
    if not root:
        return None
    if val == root.val:
        return root
    elif val < root.val:
        return self.searchBST(root.left, val)
    else:
        return self.searchBST(root.right, val)


def searchBST(self, root: TreeNode, val: int) -> TreeNode:
    while root is not None and root.val != val:
        root = root.left if val < root.val else root.right
    return root





