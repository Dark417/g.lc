# 113. 路径总和 II

def pathSum(self, root: TreeNode, sum: int) -> List[List[int]]:
    if not root: return []
    
    def dfs(node, r, l):
        left = r - node.val
        if left == 0 and not node.left and not node.right:
            self.res.append(l)
            return
        if node.left:
            cur = l.copy()
            cur.append(node.left.val)
            dfs(node.left, left, cur)
        if node.right:
            cur = l.copy()
            cur.append(node.right.val)
            dfs(node.right, left, cur)

    self.res = []
    dfs(root, sum, [root.val])
    
    return self.res


def pathSum1(self, root: TreeNode, total: int) -> List[List[int]]:
    ret = list()
    path = list()
    
    def dfs(root: TreeNode, total: int):
        if not root:
            return
        path.append(root.val)
        total -= root.val
        if not root.left and not root.right and total == 0:
            ret.append(path[:])
        dfs(root.left, total)
        dfs(root.right, total)
        path.pop()
    
    dfs(root, total)
    return ret


import collections
def pathSum2(self, root: TreeNode, total: int) -> List[List[int]]:
    ret = list()
    parent = collections.defaultdict(lambda: None)

    def getPath(node: TreeNode):
        tmp = list()
        while node:
            tmp.append(node.val)
            node = parent[node]
        ret.append(tmp[::-1])

    if not root:
        return ret
    
    que_node = collections.deque([root])
    que_total = collections.deque([0])

    while que_node:
        node = que_node.popleft()
        rec = que_total.popleft() + node.val

        if not node.left and not node.right:
            if rec == total:
                getPath(node)
        else:
            if node.left:
                parent[node.left] = node
                que_node.append(node.left)
                que_total.append(rec)
            if node.right:
                parent[node.right] = node
                que_node.append(node.right)
                que_total.append(rec)

    return ret





