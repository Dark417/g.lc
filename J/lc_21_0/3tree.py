# tree ez
# 最终返回, dfs返回
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


# 938. 二叉搜索树的范围和
# 根据范围优化搜索
def rangeSumBST(self, root, L, R):
    def dfs(node):
        if node:
            if L <= node.val <= R:
                self.ans += node.val
            if L < node.val:
                dfs(node.left)
            if node.val < R:
                dfs(node.right)

    self.ans = 0
    dfs(root)
    return self.ans



# 783. 二叉搜索树节点最小距离
# 530. 二叉搜索树的最小绝对差

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



# 897. 递增顺序查找树
# 面试题 17.12. BiNode
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























# 687. 最长同值路径
def longestUnivaluePath(self, root: TreeNode) -> int:
    def dfs(root):
        if not root:
            return 0
        else:
            left = dfs(root.left)
            right = dfs(root.right)
            ll = rr = 0
            if root.left and root.left.val == root.val:
                ll = left + 1
            if root.right and root.right.val == root.val:
                rr = right + 1
            self.mx = max(self.mx, ll + rr)
            return max(ll, rr)
                
    self.mx = 0
    dfs(root)
    return self.mx



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




























