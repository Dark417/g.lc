#543. 二叉树的直径

def diameterOfBinaryTree(self, root: TreeNode) -> int:
    self.ans = 0
    def depth(node):
        if not node:
            return 0
        L = depth(node.left)
        R = depth(node.right)
        self.ans = max(self.ans, L + R)
        return max(L, R) + 1

    depth(root)
    return self.ans


def diameterOfBinaryTree(self, root: TreeNode) -> int:
    self.ans = 1
    def depth(node):
        if not node:
            return 0
        L = depth(node.left)
        R = depth(node.right)
        self.ans = max(self.ans, L + R + 1)
        return max(L, R) + 1

    depth(root)
    return self.ans - 1


def diameterOfBinaryTree(self, root: TreeNode) -> int:
    def dfs(node):
        if not node.left and not node.right:
            return 1
        elif node.left and not node.right:
            left = dfs(node.left)
            self.m = max(self.m, left)
            return left + 1
        elif not node.left and node.right:
            right = dfs(node.right)
            self.m = max(self.m, right)
            return right + 1
        else:
            left = dfs(node.left)
            right = dfs(node.right)
            self.m = max(self.m, left + right)
            return max(left, right) + 1
    
    self.m = 0
    dfs(root)
    return self.m













