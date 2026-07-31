# 114. Flatten Binary Tree to Linked List

def flatten(self, root: TreeNode) -> None:
    preorderList = list()

    def preorderTraversal(root: TreeNode):
        if root:
            preorderList.append(root)
            preorderTraversal(root.left)
            preorderTraversal(root.right)
    
    preorderTraversal(root)
    size = len(preorderList)
    for i in range(1, size):
        prev, curr = preorderList[i - 1], preorderList[i]
        prev.left = None
        prev.right = curr


def flatten(self, root: TreeNode) -> None:
    preorderList = list()
    stack = list()
    node = root

    while node or stack:
        while node:
            preorderList.append(node)
            stack.append(node)
            node = node.left
        node = stack.pop()
        node = node.right
    
    size = len(preorderList)
    for i in range(1, size):
        prev, curr = preorderList[i - 1], preorderList[i]
        prev.left = None
        prev.right = curr


def flatten(self, root: TreeNode) -> None:
    if not root:
        return
    
    stack = [root]
    prev = None
    
    while stack:
        curr = stack.pop()
        if prev:
            prev.left = None
            prev.right = curr
        left, right = curr.left, curr.right
        if right:
            stack.append(right)
        if left:
            stack.append(left)
        prev = curr


def flattenx(self, root: TreeNode) -> None:
    if not root:
        return
    
    pre = None
    stack = [root]

    while stack:
        cur = stack.pop()
        if pre:
            pre.left = None
            pre.right = cur
        if cur.left:
            stack.append(cur.left)
        if cur.right:
            stack.append(cur.right)
        pre = cur


def flatten2(self, root: TreeNode) -> None:
    curr = root
    while curr:
        if curr.left:
            predecessor = nxt = curr.left
            while predecessor.right:
                predecessor = predecessor.right
            predecessor.right = curr.right
            curr.left = None
            curr.right = nxt
        curr = curr.right


def flatten2(self, root: TreeNode) -> None:
    cur = root
    while cur:
        if cur.left:
            pre = nxt = cur.left
            while pre.right:
                pre = pre.right
            pre.right = cur.right
            cur.right = nxt
            cur.left = None
        cur = cur.right