# 129. 求根到叶子节点数字之和

def sumNumbers(self, root: TreeNode) -> int:
    if not root:
        return 0
    
    def dfs(node, cur):
        now = cur*10 + node.val
        if not node.left and not node.right:
            self.ans += now
            return
        if node.left:
            dfs(node.left, now)
        if node.right:
            dfs(node.right, now)

    self.ans = 0
    dfs(root, 0)
    
    return self.ans


def sumNumbers(self, root: TreeNode) -> int:
    if not root:
        return 0
    
    def dfs(node, cur):
        if not node.left and not node.right:
            self.ans += cur
            return
        if node.left:
            dfs(node.left, cur*10 + node.left.val)
        if node.right:
            dfs(node.right, cur*10 + node.right.val)

    self.ans = 0
    dfs(root, root.val)
    
    return self.ans


def sumNumbers(self, root: TreeNode) -> int:
    if not root:
        return 0
    ans = 0
    cur = [[root, 0]]
    while cur:
        node, val = cur.pop()
        if not node.left and not node.right:
            ans += val*10 + node.val
        if node.left:
            cur.append([node.left, val*10 + node.val])
        if node.right:
            cur.append([node.right, val*10 + node.val])
    
    return ans


def sumNumbers(self, root: TreeNode) -> int:
    if not root:
        return 0
    ans = 0
    
    cur = [[root, root.val]]
    while cur:
        node, val = cur.pop()

        if not node.left and not node.right:
            ans += val
        if node.left:
            cur.append([node.left, val*10 + node.left.val])
        if node.right:
            cur.append([node.right, val*10 + node.right.val])
    
    return ans


# official

def sumNumbers(self, root: TreeNode) -> int:
    def dfs(root: TreeNode, prevTotal: int) -> int:
        if not root:
            return 0
        total = prevTotal * 10 + root.val
        if not root.left and not root.right:
            return total
        else:
            return dfs(root.left, total) + dfs(root.right, total)

    return dfs(root, 0)


def sumNumbers(self, root: TreeNode) -> int:
    if not root:
        return 0

    total = 0
    nodeQueue = collections.deque([root])
    numQueue = collections.deque([root.val])
    
    while nodeQueue:
        node = nodeQueue.popleft()
        num = numQueue.popleft()
        left, right = node.left, node.right
        if not left and not right:
            total += num
        else:
            if left:
                nodeQueue.append(left)
                numQueue.append(num * 10 + left.val)
            if right:
                nodeQueue.append(right)
                numQueue.append(num * 10 + right.val)

    return total

