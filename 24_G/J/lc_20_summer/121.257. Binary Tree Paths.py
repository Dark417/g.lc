"""
121.257. Binary Tree Paths 二叉树的所有路径



Given a binary tree, return all root-to-leaf paths.

Note: A leaf is a node with no children.

Example:

Input:

   1
 /   \
2     3
 \
  5

Output: ["1->2->5", "1->3"]

Explanation: All root-to-leaf paths are: 1->2->5, 1->3

"""


# 





# Stean
def binaryTreePaths(self, root):
    if not root:
        return []
    return [str(root.val) + '->' + path
            for kid in (root.left, root.right) if kid
            for path in self.binaryTreePaths(kid)] or [str(root.val)]



def rootToLeafPaths(self, root):
   if not root: return []
   if not root.left and not root.right: return [str(root.val)]
   return [str(root.val) + '->' + i for i in self.rootToLeafPaths(root.left)] +
             [str(root.val) + '->' + i for i in self.rootToLeafPaths(root.right)]



def binaryTreePaths(self, root):
    if not root: return []
    result= [ str(root.val)+"->" + path for path in self.binaryTreePaths(root.left)]
    result+= [ str(root.val)+"->" + path for path in self.binaryTreePaths(root.right)]
    return result or [str(root.val)]  # if empty return leaf itself


# caikehe
# dfs + stack
def binaryTreePaths1(self, root):
    if not root:
        return []
    res, stack = [], [(root, "")]
    while stack:
        node, ls = stack.pop()
        if not node.left and not node.right:
            res.append(ls+str(node.val))
        if node.right:
            stack.append((node.right, ls+str(node.val)+"->"))
        if node.left:
            stack.append((node.left, ls+str(node.val)+"->"))
    return res


# bfs + queue
def binaryTreePaths2(self, root):
    if not root:
        return []
    res, queue = [], collections.deque([(root, "")])
    while queue:
        node, ls = queue.popleft()
        if not node.left and not node.right:
            res.append(ls+str(node.val))
        if node.left:
            queue.append((node.left, ls+str(node.val)+"->"))
        if node.right:
            queue.append((node.right, ls+str(node.val)+"->"))
    return res


# dfs recursively
def binaryTreePaths(self, root):
    if not root:
        return []
    res = []
    self.dfs(root, "", res)
    return res

def dfs(self, root, ls, res):
    if not root.left and not root.right:
        res.append(ls+str(root.val))
    if root.left:
        self.dfs(root.left, ls+str(root.val)+"->", res)
    if root.right:
        self.dfs(root.right, ls+str(root.val)+"->", res)




def binaryTreePaths(self, root):
    if not root:
        return []
    res = []
    self.path(root,'',res)
    return res
    
def path(self,root,string,res):
    string += str(root.val)
    if root.left:
        self.path(root.left,string+'->',res)
    if root.right:
        self.path(root.right,string+'->',res)
    if not root.left and not root.right:
        res.append(string)


def binaryTreePaths(self, root):
    def rec(node,ls):
        if not node:
            return
        ls+=str(node.val)
        if not node.left and not node.right:
            res.append(ls)
        rec(node.left,ls+"->")
        rec(node.right,ls+"->")
    res = []
    rec(root,"")
    return res


def binaryTreePaths(self, root):
    res = []
    self.rec(root,"",res)
    return res
def rec(self,node,ls,res):
        if not node:
            return
        ls+=str(node.val)
        if not node.left and not node.right:
            res.append(ls)
        self.rec(node.left,ls+"->",res)
        self.rec(node.right,ls+"->",res)




































