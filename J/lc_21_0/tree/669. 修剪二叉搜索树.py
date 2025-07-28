# 669. 修剪二叉搜索树

def trimBST(self, root, L, R):
    def trim(node):
        if not node:
            return None
        elif node.val > R:
            return trim(node.left)
        elif node.val < L:
            return trim(node.right)
        else:
            node.left = trim(node.left)
            node.right = trim(node.right)
            return node

    return trim(root)




def trimBST(self, root: TreeNode, low: int, high: int) -> TreeNode:
    def dfs(root):
        if not root:
            return None
        elif root.val < low:
            root = dfs(root.right)
        elif root.val > high:
            root = dfs(root.left)  
        elif root.val >= low and root.val <= high:
            root.left = dfs(root.left)
            root.right = dfs(root.right)
        return root            

    return dfs(root)



def trimBST(self, root: TreeNode, low: int, high: int) -> TreeNode:
    def dfs(root):
        if not root:
            return None
        if root.val < low:
            root = dfs(root.right)
            return root
        if root.val > high:
            root = dfs(root.left)
            return root
        else:
            root.left = dfs(root.left)
            root.right = dfs(root.right)
            return root            

    return dfs(root)





























