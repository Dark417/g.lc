# 226. 翻转二叉树


def invertTree(self, root: TreeNode) -> TreeNode:
    if not root:
        return root
    
    left = self.invertTree(root.left)
    right = self.invertTree(root.right)
    root.left, root.right = right, left
    return root

def mirrorTree(self, root: TreeNode) -> TreeNode:
    if not root: return
    root.left, root.right = self.mirrorTree(root.right), self.mirrorTree(root.left)
    return root



def mirrorTree(self, root: TreeNode) -> TreeNode:
    if not root:
        return root
    root.left, root.right = root.right, root.left
    # if root.left:
    self.mirrorTree(root.left)
    # if root.right:
    self.mirrorTree(root.right)
    return root





def invertTree(self, root: TreeNode) -> TreeNode:
    def dfs(node):
        if node:
            left = dfs(node.left)
            right = dfs(node.right)
            node.left, node.right = right, left
        return node
    dfs(root)
    return root



# stack 
def mirrorTree(self, root: TreeNode) -> TreeNode:
    if not root: return
    stack = [root]
    while stack:
        node = stack.pop()
        if node.left: stack.append(node.left)
        if node.right: stack.append(node.right)
        node.left, node.right = node.right, node.left
    return root





























































