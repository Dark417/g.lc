# 783. 二叉搜索树节点最小距离

def minDiffInBST(self, root: TreeNode) -> int:
    def dfs(root):
        nonlocal l
        if root:
            dfs(root.left)
            l.append(root.val)
            dfs(root.right)
    l = []
    dfs(root)
    return min(l[i] - l[i-1] for i in range(1, len(l)))

        
def minDiffInBST(self, root: TreeNode) -> int:
    def dfs(root):
        nonlocal l
        if root:
            dfs(root.left)
            l.append(root.val)
            dfs(root.right)
    l = []
    dfs(root)
    # for i in range(1, len(l)):
    #     l[i] = l[i] + l[i-1]
    # l = [l[0]] + [l[i] + l[i-1] for i in range(1, len(l))]
    # return min(l)

    # return min(l[0], l[i] + l[i-1] for i in range(1, len(l)))


































