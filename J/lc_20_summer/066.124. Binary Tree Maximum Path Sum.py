"""
066.124. Binary Tree Maximum Path Sum


Given a non-empty binary tree, find the maximum path sum.

For this problem, a path is defined as any sequence of nodes from some starting node to any node in the tree along the parent-child connections. The path must contain at least one node and does not need to go through the root.

Example 1:

Input: [1,2,3]

       1
      / \
     2   3

Output: 6
Example 2:

Input: [-10,9,20,null,null,15,7]

   -10
   / \
  9  20
    /  \
   15   7

Output: 42

"""


# 当前子树的最大路径和，会去挑战 maxSum 全局变量


# official
def __init__(self):
        self.maxSum = float("-inf")

def maxPathSum(self, root: TreeNode) -> int:
    def maxGain(node):
        if not node:	#self.maxVal = root.val
            return 0

        # 递归计算左右子节点的最大贡献值
        # 只有在最大贡献值大于 0 时，才会选取对应子节点
        leftGain = max(maxGain(node.left), 0)
        rightGain = max(maxGain(node.right), 0)
        
        # 节点的最大路径和取决于该节点的值与该节点的左右子节点的最大贡献值
        priceNewpath = node.val + leftGain + rightGain
        
        # 更新答案
        self.maxSum = max(self.maxSum, priceNewpath)
    
        # 返回节点的最大贡献值
        return node.val + max(leftGain, rightGain)

    maxGain(root)
    return self.maxSum

def __init__(self):
        self.maxs = float("-inf")

def maxPathSum(self, root):
    
    def mx(node):
        if not root:
            return 0
        left = max(mx(node.left),0)
        right = max(mx(node.right),0)
        self.maxs = max(self.maxs, node.val+left+right)
        return node.val + max(left, right)
    mx(root)
    return self.maxs



# Stefan
#?
def maxPathSum(self, root):
    def maxsums(node):
        if not node:
            return [-2**31] * 2
        left = maxsums(node.left)
        right = maxsums(node.right)
        return [node.val + max(left[0], right[0], 0),
                max(left + right + [node.val + left[0] + right[0]])]
    return max(maxsums(root))



def maxPathSum(self, root):
    def maxend(node):
        if not node:
            return 0
        left = maxend(node.left)
        right = maxend(node.right)
        self.max = max(self.max, left + node.val + right)
        return max(node.val + max(left, right), 0)
    self.max = None
    maxend(root)
    return self.max


# panda
def maxPathSum(self, root: TreeNode) -> int:
    self.max_path_sum = float('-inf')

    def dfs(node):
        if not node:  # 边界情况
            return 0
        left = dfs(node.left)  # 对左右节点dfs
        right = dfs(node.right)
        cur_max = max(
            node.val,
            node.val + left,
            node.val + right,
        )
        # 更新全局变量
        self.max_path_sum = max(self.max_path_sum, cur_max, node.val + left + right)
        return cur_max

    dfs(root)
    return self.max_path_sum




def maxPathSum(self, root):
    def find_max(node):
        if not node: return 0
        left, right = find_max(node.left), find_max(node.right)
        v = max(node.val, node.val + max(left, right))
        self.ans = max(self.ans, v, left + node.val + right)
        return v
    self.ans = None
    find_max(root)
    return self.ans



def maxPathSum(self, root: TreeNode) -> int:
    def backtracking(node: TreeNode) -> tuple:
        if not node: return float('-inf'), 0
        left_so_far, left_ending_here = backtracking(node.left)
        right_so_far, right_ending_here = backtracking(node.right)
        max_so_far = max(left_so_far, right_so_far,
                         node.val + left_ending_here + right_ending_here)
        max_ending_here = max(0, node.val + max(left_ending_here, right_ending_here))
        return max_so_far, max_ending_here

    return backtracking(root)[0]



def maxPathSum(self, root) -> int:
    def re(node):
        if not node:
            return [0,float('-inf')]
        else:
            res_l = re(node.left)
            res_r = re(node.right)
            double_max = res_l[0]+res_r[0]+node.val
            single_max = max(res_l[0]+node.val,res_r[0]+node.val,node.val)
            all_max = max(double_max,single_max,res_r[1],res_l[1])
            res = [single_max,all_max]
            return res
    res = re(root)
    return res[1]




# Recursively 
def maxPathSum(self, root):
    self.res = -sys.maxsize-1
    self.oneSideSum(root)
    return self.res
    

def oneSideSum(self, root):
    if not root:
        return 0
    l = max(0, self.oneSideSum(root.left))
    r = max(0, self.oneSideSum(root.right))
    self.res = max(self.res, l+r+root.val)
    return max(l, r)+root.val



def maxPathSum(self, root):
    if not root:
        return 0
    self.res = root.val
    self.oneSum(root)
    return self.res

# compute one side maximal sum, 
# (root+left children, or root+right children),
# root is the included top-most node 
def oneSum(self, node):
    if not node:
        return 0
    l = max(0, self.oneSum(node.left))
    r = max(0, self.oneSum(node.right))
    self.res = max(self.res, node.val+l+r)
    return node.val + max(l, r)



def maxPathSum(self, root):
    self.res = - float('inf')
    self.dfs(root)
    return self.res
    
def dfs(self, root):
    if not root: return 0
    left = self.dfs(root.left)
    right = self.dfs(root.right)
    self.res = max(self.res, left + right + root.val)
    cur = max(left, right) + root.val
    return cur if cur > 0 else 0


def maxPathSum(self, root):
    def dfs(node):  # returns: max one side path sum, max path sum
        l = r = 0
        ls = rs = None
        if node.left:
            l, ls = dfs(node.left)
            l = max(l, 0)
        if node.right:
            r, rs = dfs(node.right)
            r = max(r, 0)
        return node.val + max(l, r), max(node.val + l + r, ls, rs)
    if root:
        return dfs(root)[1]
    return 0



def maxPathSum(self, root):
    def maxPathAtNode(tree_node):
        if not tree_node:
            return 0
        left = max(0, maxPathAtNode(tree_node.left))
        right = max(0, maxPathAtNode(tree_node.right))
        nonlocal max_path # Variable from outer scope.
        max_path = max(max_path, tree_node.val + left + right)
        return tree_node.val + max(left, right)
    
    max_path = root.val
    _ = maxPathAtNode(root) # Ignore the output.
    return max_path



current_max = float('-inf')
    def maxPathSum(self, root):
        self.maxPathSumHelper(root)
        return self.current_max

    def maxPathSumHelper(self, root):
        """Helper method"""
        if root is None:
            return root
        left = self.maxPathSumHelper(root.left)
        right = self.maxPathSumHelper(root.right)
        left = 0 if left is None else (left if left > 0 else 0)
        right = 0 if right is None else (right if right > 0 else 0)
        self.current_max = max(left+right+root.val, self.current_max)
        return max(left, right) + root.val



def init(self):
self.globalmax = float("-inf")

def maxPathSum(self, root):
    self.findmax(root)
    return self.globalmax

def findmax(self, node):
    if not node:
        return 0
    left = self.findmax(node.left)
    right = self.findmax(node.right)
    if left < 0: left = 0
    if right < 0: right = 0
    self.globalmax = max(left + right + node.val, self.globalmax)
    return max(left, right) + node.val

















