# 112. 路径总和


def hasPathSum(self, root: TreeNode, sum: int) -> bool:
    if not root: return False
    cur = [(root, root.val)]
    res = []
    while cur:
        node, val = cur.pop()
        if node.left:
            cur.append([node.left, node.left.val + val])
        if node.right:
            cur.append([node.right, node.right.val + val])
        if not node.left and not node.right:
            res.append(val) 

    return sum in res


def hasPathSum0(self, root: TreeNode, sum: int) -> bool:
    def dfs(node, val, res):
        if not node.left and not node.right:
            res.append(val)
        if node.left:
            dfs(node.left, val + node.left.val, res)
        if node.right:
            dfs(node.right, val + node.right.val, res)
    
    if not root: 
        return False
    res = []
    dfs(root, root.val, res)
    return sum in res


def hasPathSum1(self, root: TreeNode, sum: int) -> bool:
    if not root:
        return False
    que_node = collections.deque([root])
    que_val = collections.deque([root.val])
    while que_node:
        now = que_node.popleft()
        temp = que_val.popleft()
        if not now.left and not now.right:
            if temp == sum:
                return True
            continue
        if now.left:
            que_node.append(now.left)
            que_val.append(now.left.val + temp)
        if now.right:
            que_node.append(now.right)
            que_val.append(now.right.val + temp)
    return False


def hasPathSum2(self, root: TreeNode, sum: int) -> bool:
    if not root:
        return False
    if not root.left and not root.right:
        return sum == root.val
    return self.hasPathSum(root.left, sum - root.val) or self.hasPathSum(root.right, sum - root.val)


