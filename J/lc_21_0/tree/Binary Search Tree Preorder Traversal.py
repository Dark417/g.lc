

def preorderTraversal(self, root: TreeNode) -> List[int]:

    def stackin(node, stack):
        if node:
            stack.append(node)
        if node.left:
            stackin(node.left, stack)

    stack = []
    ret = []
    stackin(root, stack)

    while stack:
        cur = stack.pop()
        if cur:
            ret.append(cur.val)
            if cur.right:
                stackin(cur.right, stack)

    return ret














































