# 1367. 二叉树中的列表

def dfs(self, head: ListNode, rt: TreeNode) -> bool:
    if not head:
        return True
    if not rt:
        return False
    # if rt.val != head.val:
    #     return False
    # return self.dfs(head.next, rt.left) or self.dfs(head.next, rt.right)
    return root.val == head.val and (dfs(head.next, 
    	root.left) or dfs(head.next, root.right))

    
def isSubPath(self, head: ListNode, root: TreeNode) -> bool:
    if not root:
        return False
    return self.dfs(head, root) or self.isSubPath(head, root.left) or self.isSubPath(head, root.right)









def isSubPath(self, head, root):
    A, dp = [head.val], [0]
    i = 0
    node = head.next
    while node:
        while i and node.val != A[i]:
            i = dp[i - 1]
        i += node.val == A[i]
        A.append(node.val)
        dp.append(i)
        node = node.next

    def dfs(root, i):
        if not root: return False
        while i and root.val != A[i]:
            i = dp[i - 1]
        i += root.val == A[i]
        return i == len(dp) or dfs(root.left, i) or dfs(root.right, i)
    return dfs(root, 0)






