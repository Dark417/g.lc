"""
119.129. Sum Root to Leaf Numbers
求根到叶子节点数字之和

Given a binary tree containing digits from 0-9 only, each root-to-leaf path could represent a number.

An example is the root-to-leaf path 1->2->3 which represents the number 123.

Find the total sum of all root-to-leaf numbers.

Note: A leaf is a node with no children.

Example:

Input: [1,2,3]
    1
   / \
  2   3
Output: 25
Explanation:
The root-to-leaf path 1->2 represents the number 12.
The root-to-leaf path 1->3 represents the number 13.
Therefore, sum = 12 + 13 = 25.
Example 2:

Input: [4,9,0,5,1]
    4
   / \
  9   0
 / \
5   1
Output: 1026
Explanation:
The root-to-leaf path 4->9->5 represents the number 495.
The root-to-leaf path 4->9->1 represents the number 491.
The root-to-leaf path 4->0 represents the number 40.
Therefore, sum = 495 + 491 + 40 = 1026.

"""


def sumNumbers(self, root: TreeNode) -> int:
    if not root: return 0
    cur = [(root, [root.val])]
    res = []
    while cur:
        node, li = cur.pop(0)
        if not node.left and not node.right:
            res.append(li)
        if node.left:
            cur.append((node.left, li+[node.left.val]))
        if node.right:
            cur.append((node.right, li+[node.right.val]))
    return sum(int("".join(str(i) for i in l)) for l in res)
    return sum(map(lambda x: int("".join(str(i) for i in x)), res))



def sumNumbers(self, root: TreeNode) -> int:
    if not root: return 0
    def dfs(node, l):
        if not node.left and not node.right:
            res.append(l)
        if node.left:
            dfs(node.left, l+[node.left.val])
        if node.right:
            dfs(node.right, l+[node.right.val])
    res = []
    dfs(root, [root.val])
    return sum(map(lambda x: int("".join(str(i) for i in x)), res))
        


#
def sumNumbers(self, root):
	def dfs(node, sum):
		if not node: return 0
		cur = sum*10 + node.val
		if not node.left and not node.right:
			return cur
		return dfs(node.left, cur) + dfs(node.right, cur)
	return dfs(root, 0)


#
def sumNumbers(self, root: TreeNode) -> int:
        if not root:
            return 0
        res = []
        tmp = []
        def dfs(node):
            if not node: return
            tmp.append(node.val)
            if (node.left, node.right) == (None, None):
                res.append(tmp.copy())
            else:
                dfs(node.left)
                dfs(node.right)
            tmp.pop()
        dfs(root)
        return sum(map(lambda x: int("".join(str(i) for i in x)), res))




def sumNumbers(self, root: TreeNode) -> int:
    if not root:
        return 0
    self.res = 0
    def help(root,tmp):
        if not root.left and not root.right:
            self.res += int(tmp)
        #if root.left:
        help(root.left,tmp+str(root.left.val))
        #if root.right:
        help(root.right,tmp+str(root.right.val))
    help(root,str(root.val))
    return self.res





def sumNumbers(self, root: TreeNode) -> int:
	tmp = lambda self, root: [] if not root else [root.val] if not root.left and not root.right \
                             else [str(root.val)+str(i) for i in self.tmp(root.left)+self.tmp(root.right)]
    sumNumbers = lambda self, root: sum(map(int, self.tmp(root)))



# caikehe
# dfs + stack
def sumNumbers1(self, root):
    if not root:
        return 0
    stack, res = [(root, root.val)], 0
    while stack:
        node, value = stack.pop()
        if node:
            if not node.left and not node.right:
                res += value
            if node.right:
                stack.append((node.right, value*10+node.right.val))
            if node.left:
                stack.append((node.left, value*10+node.left.val))
    return res
    
# bfs + queue
def sumNumbers2(self, root):
    if not root:
        return 0
    queue, res = collections.deque([(root, root.val)]), 0
    while queue:
        node, value = queue.popleft()
        if node:
            if not node.left and not node.right:
                res += value
            if node.left:
                queue.append((node.left, value*10+node.left.val))
            if node.right:
                queue.append((node.right, value*10+node.right.val))
    return res
    
# recursively 
def sumNumbers(self, root):
    self.res = 0
    self.dfs(root, 0)
    return self.res
    
def dfs(self, root, value):
    if root:
        #if not root.left and not root.right:
        #    self.res += value*10 + root.val
        self.dfs(root.left, value*10+root.val)
        #if not root.left and not root.right:
        #    self.res += value*10 + root.val
        self.dfs(root.right, value*10+root.val)
        if not root.left and not root.right:
            self.res += value*10 + root.val



































