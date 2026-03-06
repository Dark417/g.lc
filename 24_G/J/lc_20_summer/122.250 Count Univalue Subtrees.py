"""
122.250	Count Univalue Subtrees
统计同值子树



"""

# NLBL
def countUnivalSubtrees(self, root):
    if root is None: return 0
    count = 0
    is_uni(root)
    return count

def is_uni(self, node):
    # base case - if the node has no children this is a univalue subtree
    if node.left is None and node.right is None:
        # found a univalue subtree - increment
        count += 1
        return True
    is_uni = True
    # check if all of the node's children are univalue subtrees and if they have the same value
    # also recursively call is_uni for children
    if node.left is not None:
        is_uni = is_uni(node.left) and is_uni and node.left.val == node.val
    if node.right is not None:
        is_uni = is_uni(node.right) and is_uni and node.right.val == node.val
    # increment res and return whether a univalue tree exists here
    count += is_uni
    return is_uni



def countUnivalSubtrees(self, root):
    count = 0
    is_valid_part(root, 0)
    return count

def is_valid_part(self, node, val):
    # considered a valid subtree
    if node is None: return True
    # check if node.left and node.right are univalue subtrees of value node.val
    if not all([is_valid_part(node.left, node.val),
                is_valid_part(node.right, node.val)]):
        return False
    # if it passed the last step then this a valid subtree - increment
    count += 1
    # at this point we know that this node is a univalue subtree of value node.val
    # pass a boolean indicating if this is a valid subtree for the parent node
    return node.val == val

# combine cases
# return T/F by ==
# 



def countUnivalSubtrees(self, root: TreeNode) -> int:
    self.summ = 0
    def dfs(node):
    if node:
        if not node.left and not node.right:
        if not node.left and node.right:
            if node.val == node.right.val and dfs(node.right):
        if not node.right and node.left:
            if node.val == node.left.val and dfs(node.left):
        if node.left and node.right:
            if dfs(node.left) and dfs(node.right) and node.val == node.left.val and node.val == node.right.val:
# multiple if operand, check in order, won't recurse if any false



def countUnivalSubtrees(self, root: TreeNode) -> int:
        self.res = 0
        def dfs(node):
            if not node: return (0, 0)
            l, ll = dfs(node.left)

            r, rr = dfs(node.right)

            if not node.left and not node.right:
                return (1, 1)
            elif not node.left and node.right:
                if rr and node.val == node.right.val:
                    return (r + 1, 1)
                else:
                    return (r, 0)
            elif not node.right and node.left:
                if ll and node.val == node.left.val:
                    return (l + 1, 1)
                else:
                    return (l, 0)
            else:
                if l and r and node.val == node.left.val and node.val == node.right.val:
                    return (l + r + 1, 1)
                else:
                    return (l + r, 0)
        
        return dfs(root)[0]




def countUnivalSubtrees(self, root: TreeNode) -> int:
    self.summ = 0
    def dfs(node):
        # or nonlocal summ
        if node:
            if not node.left and not node.right:
                self.summ += 1
                return True
            if not node.left and node.right:
                r = dfs(node.right)
                if r and node.val == node.right.val:
                    self.summ += 1
                    return True
                else:
                    return False
            if not node.right and node.left:
                l = dfs(node.left)
                if  l and node.val == node.left.val:
                    self.summ += 1
                    return True
                else:
                    return False
            if node.left and node.right:
                l = dfs(node.left)
                r = dfs(node.right)
                if l and r and node.val == node.left.val and node.val == node.right.val:
                    self.summ += 1
                    return True
                else:
                    return False
    dfs(root)
    return self.summ



def countUnivalSubtrees(self, root: TreeNode) -> int:
    self.summ = 0
    def dfs(node):
        # or nonlocal summ
        if node:
            l = dfs(node.left)
            r = dfs(node.right)
            if not node.left and not node.right:
                self.summ += 1
                return True
            if not node.left and node.right:
                if r and node.val == node.right.val:
                    self.summ += 1
                    return True
                else:
                    return False
            if not node.right and node.left:
                if  l and node.val == node.left.val:
                    self.summ += 1
                    return True
                else:
                    return False
            if node.left and node.right:
                if l and r and node.val == node.left.val and node.val == node.right.val:
                    self.summ += 1
                    return True
                else:
                    return False
    dfs(root)
    return self.summ













































