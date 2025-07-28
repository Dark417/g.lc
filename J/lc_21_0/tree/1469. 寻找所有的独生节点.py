# 1469. 寻找所有的独生节点


def getLonelyNodes(self, root: TreeNode) -> List[int]:
    def dfs(node):
        if node:
            if node.left and not node.right:
                self.l.append(node.left.val)
            if node.right and not node.left:
                self.l.append(node.right.val)
            dfs(node.left)
            dfs(node.right)
    self.l = []
    dfs(root)
    return self.l











