# 面试题 04.04. 检查平衡性

def isBalanced(self, root: TreeNode) -> bool:
    def dfs(node):
        if node:
            left = dfs(node.left)
            right = dfs(node.right)
            return (left[0] and right[0] and abs(left[1] - right[1])<=1, max(left[1], right[1]) + 1)
        else:
            return (True, 0)
    return dfs(root)[0]


        
def isBalanced(self, root: TreeNode) -> bool:
    def height(root: TreeNode) -> int:
        if not root:
            return 0
        return max(height(root.left), height(root.right)) + 1

    if not root:
        return True
    return abs(height(root.left) - height(root.right)) <= 1 and self.isBalanced(root.left) and self.isBalanced(root.right)



def isBalanced(self, root: TreeNode) -> bool:
    def height(root: TreeNode) -> int:
        if not root:
            return 0
        leftHeight = height(root.left)
        rightHeight = height(root.right)
        if leftHeight == -1 or rightHeight == -1 or abs(leftHeight - rightHeight) > 1:
            return -1
        else:
            return max(leftHeight, rightHeight) + 1

    return height(root) >= 0





