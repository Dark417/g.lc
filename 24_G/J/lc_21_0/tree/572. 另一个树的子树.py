# 572. 另一个树的子树

def isSubtree(self, s: TreeNode, t: TreeNode) -> bool:
    if s == None: return False
    def check(s, t):
        if not s and not t: return True
        if not s or not t: return False
        if s.val == t.val:
            return check(s.left, t.left) and check(s.right, t.right)
        return False
    return check(s, t) or self.isSubtree(s.left, t) or self.isSubtree(s.right, t)


def isSubtree(self, s, t):
    # if not s and not t:
    #     return True
    # if not s or not t:
    #     return False
    if not s:
        return False
    return self.isSameTree(s, t) or self.isSubtree(s.left, t) or self.isSubtree(s.right, t)
        
def isSameTree(self, s, t):
    if not s and not t:
        return True
    if not s or not t:
        return False
    return s.val == t.val and self.isSameTree(s.left, t.left) and self.isSameTree(s.right, t.right)


