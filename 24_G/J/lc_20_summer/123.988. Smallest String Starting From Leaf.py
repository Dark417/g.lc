"""
123.988. Smallest String Starting From Leaf
从叶结点开始的最小字符串

Given the root of a binary tree, each node has a value from 0 to 25 representing the 
letters 'a' to 'z': a value of 0 represents 'a', a value of 1 represents 'b', and so on.

Find the lexicographically smallest string that starts at a leaf of this tree and ends at the root.

(As a reminder, any shorter prefix of a string is lexicographically smaller: for 
example, "ab" is lexicographically smaller than "aba".  A leaf of a node is a node that has no children.)

 

Example 1:



Input: [0,1,2,3,4,3,4]
Output: "dba"
Example 2:



Input: [25,1,3,1,3,0,2]
Output: "adz"
Example 3:



Input: [2,2,1,null,1,0,null,0]
Output: "abc"
 

Note:

The number of nodes in the given tree will be between 1 and 8500.
Each node in the tree will have a value between 0 and 25.

"""

chr(ord('z') + 1)


def smallestFromLeaf(self, root: TreeNode) -> str:
    if not root: return ""
    s = "abcdefghijklmnopqrstuvwxyz"
    cur = [(root, [s[root.val]])]
    res = []
    while cur:
        node, l = cur.pop(0)
        if not node.left and not node.right:
            res.append(l)
        if node.left:
            cur.append((node.left, [s[node.left.val]] + l))
        if node.right:
            cur.append((node.right, [s[node.right.val]] + l))
    return min("".join(l) for l in res)



def smallestFromLeaf(self, root: TreeNode) -> str:
    if not root: return ""
    s = "abcdefghijklmnopqrstuvwxyz"
    cur = [(root, [root.val])]
    res = []
    while cur:
        node, l = cur.pop(0)
        if not node.left and not node.right:
            res.append(l)
        if node.left:
            cur.append((node.left, [node.left.val] + l))
        if node.right:
            cur.append((node.right, [node.right.val] + l))
    return min("".join(str(s[i]) for i in l)  for l in res)


def smallestFromLeaf(self, root: TreeNode) -> str:
    if not root: return ""
    s = "abcdefghijklmnopqrstuvwxyz"
    cur = [(root, [root.val])]
    res = "z"*9
    while cur:
        node, l = cur.pop(0)
        if not node.left and not node.right:
            tmp = "".join(s[i] for i in l)
            res = min(res, tmp)
        if node.left:
            cur.append((node.left, [node.left.val] + l))
        if node.right:
            cur.append((node.right, [node.right.val] + l))
    return res


def smallestFromLeaf(self, root: TreeNode) -> str:
    s = "abcdefghijklmnopqrstuvwxyz"
    self.res = "z"
    def dfs(node, l):
        if not root: return
        if not node.left and not node.right:
            tmp = "".join(s[i] for i in l)
            self.res = min(self.res, tmp)
        if node.left:
            dfs(node.left, [node.left.val] + l)
        if node.right:
            dfs(node.right, [node.right.val] + l)
    dfs(root, [root.val])
    return self.res



def smallestFromLeaf(self, node: 'TreeNode') -> 'str':
    if not node: return ''
    left = self.smallestFromLeaf(node.left)
    right = self.smallestFromLeaf(node.right)
    return (left if right == '' or (left != '' and left < right) else right) + chr(97+node.val)



def smallestFromLeaf(self, node: 'TreeNode') -> 'str':
    def dfs(node, path):
        if not node.left and not node.right:
            self.res = min(self.res, path[::-1])
        if node.left:
            dfs(node.left, path + chr(ord("a")+node.left.val))
        if node.right:
            dfs(node.right, path + chr(ord("a")+node.right.val))
    self.res = "z" * 8500
    dfs(root, chr(ord("a")+root.val))
    return self.res



def smallestFromLeaf(self, root):
    self.ans = "~"
    def dfs(node, A):
        if node:
            A.append(chr(node.val + ord('a')))
            #A = [chr(node.val + ord('a'))] + A

            if not node.left and not node.right:
                self.ans = min(self.ans, "".join(reversed(A)))
                #self.ans = min(self.ans, "".join(A))
            dfs(node.left, A)
            dfs(node.right, A)
            A.pop()

    dfs(root, [])
    return self.ans


def smallestFromLeaf(self, root: TreeNode) -> str:
    def dfs(root,s):
        if not root.left and not root.right:
            return (chr(97+root.val)+s)
        if root.left and root.right:
            L = dfs(root.left,chr(97+root.val)+s)
            R = dfs(root.right,chr(97+root.val)+s)
            return min(L,R)
        elif root.left:
            return dfs(root.left,chr(97+root.val)+s)
        else:
            return dfs(root.right,chr(97+root.val)+s)
    return dfs(root,'')


def smallestFromLeaf(self, root: TreeNode) -> str:
    def dfs(root):
        alpha = chr(root.val+97)
        if not root.left and not root.right:
            return {alpha}
        if not root.left:
            return map(lambda i: i+alpha, dfs(root.right))
        if not root.right:
            return map(lambda i: i+alpha, dfs(root.left))
        return map(lambda i: i+alpha, set(dfs(root.right)) | set(dfs(root.left)))

    if not root:
        return ''
    return min(dfs(root))













































