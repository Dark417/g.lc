# 111. 二叉树的最小深度


def minDepth(self, root: TreeNode) -> int:
    if not root:
        return 0
    def dfs(node, lv):
        if node:
            if not node.left and not node.right:
                self.m = min(self.m, lv)
            dfs(node.left, lv+1)
            dfs(node.right, lv+1)
    self.m = float("inf")
    dfs(root, 1)
    return self.m



def minDepth(self, root: TreeNode) -> int:
    if not root:
        return 0
    
    if not root.left and not root.right:
        return 1
    
    min_depth = 10**9
    if root.left:
        min_depth = min(self.minDepth(root.left), min_depth)
    if root.right:
        min_depth = min(self.minDepth(root.right), min_depth)
    
    return min_depth + 1



def minDepth(self, root: TreeNode) -> int:
    if not root:
        return 0

    que = collections.deque([(root, 1)])
    while que:
        node, depth = que.popleft()
        if not node.left and not node.right:
            return depth
        if node.left:
            que.append((node.left, depth + 1))
        if node.right:
            que.append((node.right, depth + 1))
    
    return 0

















