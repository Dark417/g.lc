# 250. 统计同值子树

def countUnivalSubtrees(self, root: TreeNode) -> int:
    self.ans = 0
    
    def dfs(node):
        if node:
            if not node.left and not node.right:
                self.ans += 1
                return True

            left = dfs(node.left)
            right = dfs(node.right)
            
            if node.left and node.right:
                if node.val == node.left.val and node.val == node.right.val and left and right:
                    self.ans += 1
                    return True
            elif node.left and node.val == node.left.val and left:
                self.ans += 1
                return True
            elif node.right and node.val == node.right.val and right:
                self.ans += 1
                return True
    dfs(root)
    return self.ans

# upgrade
def countUnivalSubtreesx(self, root: TreeNode) -> int:
    if not root: return 0
    self.ans = 0
    
    def dfs(node):
        if not node.left and not node.right:
            self.ans += 1
            return True

        left = dfs(node.left)
        right = dfs(node.right)
        
        if node.left and node.right:
            if node.val == node.left.val and node.val == node.right.val and left and right:
                self.ans += 1
                return True
        elif node.left and node.val == node.left.val and left:
            self.ans += 1
            return True
        elif node.right and node.val == node.right.val and right:
            self.ans += 1
            return True
    dfs(root)
    return self.ans



def countUnivalSubtrees0(self, root):
    if root is None: return 0
    self.count = 0
    self.is_uni(root)
    return self.count

def is_uni(self, node):
    if node.left is None and node.right is None:
        self.count += 1
        return True
    is_uni = True           # update
    if node.left is not None:
        is_uni = self.is_uni(node.left) and is_uni and node.left.val == node.val
    if node.right is not None:
        is_uni = self.is_uni(node.right) and is_uni and node.right.val == node.val

    self.count += is_uni
    return is_uni

    
def countUnivalSubtrees1(self, root):
    self.count = 0
    self.is_valid_part(root, 0)
    return self.count

def is_valid_part(self, node, val):
    if node is None: return True
    if not all([self.is_valid_part(node.left, node.val),
                self.is_valid_part(node.right, node.val)]):
        return False

    self.count += 1
    return node.val == val
