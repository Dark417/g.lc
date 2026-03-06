"""
118.113. Path Sum II
路径总和

Given a binary tree and a sum, find all root-to-leaf paths where each path's sum equals the given sum.

Note: A leaf is a node with no children.

Example:

Given the below binary tree and sum = 22,

      5
     / \
    4   8
   /   / \
  11  13  4
 /  \    / \
7    2  5   1
Return:

[
   [5,4,11,2],
   [5,8,4,5]
]

"""

# D

def pathSum(self, root: TreeNode, sum: int) -> List[List[int]]:
    if not root: return []
    res = []
    def rec(node, curv, path):
        if not node: return
        else:
            curv = curv - node.val
            if not node.left and not node.right and curv == 0:
                path.append(node.val)
                res.append(path)
            else:
                if node.left:
                    rec(node.left, curv, path + [node.val])
                if node.right:
                    rec(node.right, curv, path + [node.val])
    rec(root, sum, [])
    return res
# remove if ... let recursion check


def pathSum(self, root: TreeNode, sum: int) -> List[List[int]]:
    if not root: return []
    res = []
    cur = [(root, sum, [])]
    lnext = []
    while cur:
        while cur:
            node, curv, path = cur.pop(0)
            curv = curv - node.val
            if not node.left and not node.right and curv == 0:
                path += [node.val]
                res.append(path)
            else:
                if node.left:
                    lnext.append((node.left, curv, path+[node.val]))
                if node.right:
                    lnext.append((node.right, curv, path+[node.val]))
        cur = lnext
        lnext = []
    return res



def pathSum(self, root: TreeNode, sum: int) -> List[List[int]]:
    if not root: return []
    res = []
    cur = [(root, sum, [])]
    lnext = []
    while cur:
        while cur:
            node, curv, path = cur.pop(0)
            curv = curv - node.val
            if not node.left and not node.right and curv == 0:
                path += [node.val]
                res.append(path)
            else:
                if node.left:
                    lnext.append((node.left, curv, path+[node.val]))
                if node.right:
                    lnext.append((node.right, curv, path+[node.val]))
        cur = lnext
        lnext = []
    return res



def pathSum(self, root: TreeNode, sum: int) -> List[List[int]]:
    if not root: return []
    res = []
    cur = [(root, sum, [])]
    lnext = []
    while cur:
        node, curv, path = cur.pop(0)
        curv = curv - node.val
        if not node.left and not node.right and curv == 0:
            path += [node.val]
            res.append(path)
        else:
            if node.left:
                cur.append((node.left, curv, path+[node.val]))
            if node.right:
                cur.append((node.right, curv, path+[node.val]))
    return res


# backtrack
def pathSum(self, R: TreeNode, S: int) -> List[List[int]]:
    A, P = [], []
    def dfs(N):
        if N == None: return
        P.append(N.val)
        if (N.left,N.right) == (None,None) and sum(P) == S: A.append(list(P))
        else: dfs(N.left), dfs(N.right)
        P.pop()
    dfs(R)
    return A


def pathSum2(self, root, sum):
    if not root:
        return []
    if not root.left and not root.right and sum == root.val:
        return [[root.val]]
    tmp = self.pathSum(root.left, sum-root.val) + self.pathSum(root.right, sum-root.val)
    return [[root.val]+i for i in tmp]


# caikehe
def pathSum(self, root, sum):
    if not root:
        return []
    res = []
    self.dfs(root, sum, [], res)
    return res
    
def dfs(self, root, sum, ls, res):
    if not root.left and not root.right and sum == root.val:
        ls.append(root.val)
        res.append(ls)
    if root.left:
        self.dfs(root.left, sum-root.val, ls+[root.val], res)
    if root.right:
        self.dfs(root.right, sum-root.val, ls+[root.val], res)


def pathSum1(self, root, sum):
    res = []
    self.dfs(root, sum, [], res)
    return res
    
def dfs(self, root, sum, path, res):
    if root:
        if sum == root.val and not root.left and not root.right:
            res.append(path+[root.val])
        self.dfs(root.left, sum-root.val, path+[root.val], res)
        self.dfs(root.right, sum-root.val, path+[root.val], res)




def pathSum(self, root, sum):
    res, queue = [], collections.deque([(root, sum, [])])
    while queue:
        node, sum, path = queue.popleft()
        if node:
            if node.val == sum and not node.left and not node.right:
                res.append(path+[node.val])
                continue
            queue.append((node.left, sum-node.val, path+[node.val]))
            queue.append((node.right, sum-node.val, path+[node.val]))
    return res


# BFS + queue    
def pathSum3(self, root, sum): 
    if not root:
        return []
    res = []
    queue = [(root, root.val, [root.val])]
    while queue:
        curr, val, ls = queue.pop(0)
        if not curr.left and not curr.right and val == sum:
            res.append(ls)
        if curr.left:
            queue.append((curr.left, val+curr.left.val, ls+[curr.left.val]))
        if curr.right:
            queue.append((curr.right, val+curr.right.val, ls+[curr.right.val]))
    return res
    
# DFS + stack I  
def pathSum4(self, root, sum): 
    if not root:
        return []
    res = []
    stack = [(root, sum-root.val, [root.val])]
    while stack:
        curr, val, ls = stack.pop()
        if not curr.left and not curr.right and val == 0:
            res.append(ls)
        if curr.right:
            stack.append((curr.right, val-curr.right.val, ls+[curr.right.val]))
        if curr.left:
            stack.append((curr.left, val-curr.left.val, ls+[curr.left.val]))
    return res 

def pathSum2(self, root, sum):
    res, stack = [], [(root, sum, [])]
    while stack:
        node, sum, path = stack.pop()
        if node:
            if node.val == sum and not node.left and not node.right:
                res.append(path+[node.val])
            stack.append((node.right, sum-node.val, path+[node.val]))
            stack.append((node.left, sum-node.val, path+[node.val]))
    return res


# DFS + stack II   
def pathSum5(self, root, s): 
    if not root:
        return []
    res = []
    stack = [(root, [root.val])]
    while stack:
        curr, ls = stack.pop()
        if not curr.left and not curr.right and sum(ls) == s:
            res.append(ls)
        if curr.right:
            stack.append((curr.right, ls+[curr.right.val]))
        if curr.left:
            stack.append((curr.left, ls+[curr.left.val]))
    return res


# OTHERS
def pathSum(self, root, sum):
    if not root:
        return []
    elif not root.left and not root.right:
        if root.val == sum:
            return [[root.val]]
        else:
            return []
    l = self.pathSum(root.left, sum - root.val)
    r = self.pathSum(root.right, sum - root.val)
    resL = [[root.val]+x for x in l]
    resR = [[root.val]+x for x in r]
    return resL + resR


























