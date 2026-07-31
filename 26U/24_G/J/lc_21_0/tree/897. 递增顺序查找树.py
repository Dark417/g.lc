# 897. 递增顺序查找树

def increasingBST(self, root):
    def inorder(node):
        if node:
            inorder(node.left)
            node.left = None
            self.cur.right = node
            self.cur = node
            inorder(node.right)

    ans = self.cur = TreeNode(None)
    inorder(root)
    return ans.right



def increasingBST(self, root: TreeNode) -> TreeNode:
    def dfs(root):
        nonlocal l
        if root:
            dfs(root.left)
            l.append(root.val)
            dfs(root.right)
    l = []
    dfs(root)
    
    init = cur = TreeNode(-1)
    for i in range(len(l)):
        cur.right = TreeNode(l[i])
        cur = cur.right
    return init.right


def increasingBST(self, root: TreeNode) -> TreeNode:
    def dfs(root):
        nonlocal l
        if root:
            dfs(root.left)
            l.append(root.val)
            dfs(root.right)
    l = []
    dfs(root)
    
    init = pre = TreeNode(-1)
    for i in range(len(l)):
        cur = TreeNode(l[i])
        pre.right = cur
        pre = cur
    return init.right




























