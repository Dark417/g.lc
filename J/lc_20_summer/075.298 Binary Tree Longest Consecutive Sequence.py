"""
075.298	Binary Tree Longest Consecutive Sequence
二叉树最长连续序列

给你一棵指定的二叉树，请你计算它最长连续序列路径的长度。

该路径，可以是从某个初始结点到树中任意结点，通过「父 - 子」关系连接而产生的任意路径。

这个最长连续的路径，必须从父结点到子结点，反过来是不可以的。

示例 1：

输入:

   1
    \
     3
    / \
   2   4
        \
         5

输出: 3

解析: 当中，最长连续序列是 3-4-5，所以返回结果为 3
示例 2：

输入:

   2
    \
     3
    / 
   2    
  / 
 1

输出: 2 

解析: 当中，最长连续序列是 2-3。注意，不是 3-2-1，所以返回 2。

"""

# official

def longestConsecutive(self, root: TreeNode) -> int:
    def dfs(node, parent, l):
        nonlocal vm
        if node:
            if parent and node.val == parent.val+1:
                l+=1
            else:
                l=1
            vm = max(vm, l)
            dfs(node.left, node, l)
            dfs(node.right, node, l)
    vm = 0	# assign before calling func
    dfs(root, None, 0)
    return vm

def longestConsecutive(self, root: TreeNode) -> int:
	def dfs(node, parent, l):
		if node:
			if parent and node.val == parent.val+1:
	            l+=1
	        else:
	            l=1
	        return max(l, max(dfs(node.left, parent, l), dfs(node.right, parent, l)))

	return dfs(root, None, 0)

"""
top-down
1
private int maxLength = 0;
public int longestConsecutive(TreeNode root) {
    dfs(root, null, 0);
    return maxLength;
}

private void dfs(TreeNode p, TreeNode parent, int length) {
    if (p == null) return;
    length = (parent != null && p.val == parent.val + 1) ? length + 1 : 1;
    maxLength = Math.max(maxLength, length);
    dfs(p.left, p, length);
    dfs(p.right, p, length);
}


2
public int longestConsecutive(TreeNode root) {
    return dfs(root, null, 0);
}

private int dfs(TreeNode p, TreeNode parent, int length) {
    if (p == null) return length;
    length = (parent != null && p.val == parent.val + 1) ? length + 1 : 1;
    return Math.max(length, Math.max(dfs(p.left, p, length),
                                     dfs(p.right, p, length)));
}


"""


def longestConsecutive(self, root: TreeNode) -> int:
    def dfs(node):
        nonlocal vm
        if not node: return 0
        l = dfs(node.left) + 1
        r = dfs(node.right) + 1
        if node.left and node.left.val != node.val + 1:
        	l = 1
        if node.right and node.right.val != node.val + 1:
        	r = 1
        cur = max(l, r)
        vm = max(vm, cur)
        return cur
        
    vm = 0
    dfs(root)
    return vm

"""
bottom-up
private int maxLength = 0;
public int longestConsecutive(TreeNode root) {
    dfs(root);
    return maxLength;
}

private int dfs(TreeNode p) {
    if (p == null) return 0;
    int L = dfs(p.left) + 1;
    int R = dfs(p.right) + 1;
    if (p.left != null && p.val + 1 != p.left.val) {
        L = 1;
    }
    if (p.right != null && p.val + 1 != p.right.val) {
        R = 1;
    }
    int length = Math.max(L, R);
    maxLength = Math.max(maxLength, length);
    return length;
}


"""




# D

# out
# def longestConsecutive(self, root):
#     if not root: return 0
#     v = 1
#     cur = [(root,1)]
#     lnext = []
#     while cur:
#         for _ in range(len(cur)):
#             node, l = cur.pop(0)
#             va = node.val
#             if node.left:
#                 if node.left.val == va+1:
#                     lnext.append((node.left, l+1))
#                     v = max(v, l+1)
#                 else:
#                     lnext.append((node.left,1))
#             if node.right:
#                 if node.right.val == va+1:
#                     lnext.append((node.right, l+1))
#                     v = max(v, l+1)
#                 else:
#                     lnext.append((node.right,1))
#         cur = lnext
#         lnext = []
#     return v


def longestConsecutive(self, root):
    if not root: return 0
    v = 1
    cur = [(root,1)]
    lnext = []
    while cur:
        node, l = cur.pop(0)
        va = node.val
        if node.left:
            if node.left.val == va+1:
                cur.append((node.left, l+1))
                v = max(v, l+1)
            else:
                cur.append((node.left,1))
        if node.right:
            if node.right.val == va+1:
                cur.append((node.right, l+1))
                v = max(v, l+1)
            else:
                cur.append((node.right,1))
    return v



def longestConsecutive(self, root):
    if not root: return 0
    v = 1
    cur = [(root,1)]
    lnext = []
    while cur:
        node, l = cur.pop()
        va = node.val
        if node.left:
            if node.left.val == va+1:
                cur.append((node.left, l+1))
                v = max(v, l+1)
            else:
                cur.append((node.left,1))
        if node.right:
            if node.right.val == va+1:
                cur.append((node.right, l+1))
                v = max(v, l+1)
            else:
                cur.append((node.right,1))
    return v


#
def longestConsecutive(self, root: TreeNode) -> int:
    if not root:
        return 0
    vm = 1
    def dfs(node, l):
        nonlocal vm
        if node:
            if node.left:
                if node.left.val == node.val+1:
                    vm = max(vm, l+1)
                    dfs(node.left, l+1)
                else:
                    dfs(node.left, 1)
            if node.right:
                if node.right.val == node.val+1:
                    vm = max(vm, l+1)
                    dfs(node.right, l+1)
                else:
                    dfs(node.right, 1)
    dfs(root, 1)
    return vm


#
def longestConsecutive(self, root: TreeNode) -> int:
    self.res = 0
    if not root:
        return 0
    def help(root,cur):
        if not root:
            return 
        if not root.right and not root.left:
            self.res = max(self.res,cur)
        if root.right:
            if root.right.val == root.val+1:
                help(root.right,cur+1)
                self.res = max(self.res,cur+1)
            else:
                help(root.right,1)
        if root.left:
            if root.left.val == root.val+1:
                help(root.left,cur+1)
                self.res = max(self.res,cur+1)
            else:
                help(root.left,1)
        
    help(root,1)        
    return self.res


# dfs
def longestConsecutive(self, root: TreeNode) -> int:
    if not root:
        return 0
    ans = 0

    def dfs(node, parent, parent_path):
        nonlocal ans
        if node:
	        cur = 1
	        if node.val == parent + 1:
	            cur += parent_path

	        ans = max(ans, cur)
	        dfs(node.left, node.val, cur)
	        dfs(node.right, node.val, cur)

    dfs(root, root.val + 1, 0)
    return ans


#
def longestConsecutive(self, root):
    self.Max = 0
    self.helper(root, None, 0)
    return self.Max
def helper(self, root, father, length):
    if root == None:
        return
    length = length + 1 if father == None or father != None and father.val == root.val - 1 else 1
    self.Max = max(self.Max, length)
    self.helper(root.left, root, length)
    self.helper(root.right, root, length)


# non-intuitive
def longestConsecutive(self, root: TreeNode) -> int:
    def dfs(node, last, length):
        nonlocal res
        if last + 1 == node.val:
            if not (node.left or node.right):
                res = max(res, length + 1)
            if node.left:
                dfs(node.left, node.val, length + 1)
            if node.right:
                dfs(node.right, node.val, length + 1)
        else:
            res = max(res, length)
            if node.left:
                dfs(node.left, node.val, 1)
            if node.right:
                dfs(node.right, node.val, 1)
        
    res = 0
    if root:
        dfs(root, root.val, 1)
    return res




# good
def longestConsecutive(self, root):
    self.len = 0
    def helper(root):
        if not root:
            return 0
        left = helper(root.left)
        right = helper(root.right)
        cur_len = 1
        if root.left and root.left.val == root.val + 1:
            cur_len = max(cur_len,left + 1)
        if root.right and root.right.val == root.val + 1:
            cur_len = max(cur_len,right + 1)
        self.len = max(self.len,cur_len,left,right)
        return cur_len
    helper(root)
    return self.len



# bad
def longestConsecutive(self, root):
    self.fullMax = 0
    self.helper(root)
    return self.fullMax

def helper(self, root):
    if root == None:
        return 0
    left = self.helper(root.left) + 1
    right = self.helper(root.right) + 1
    if root.left != None and root.val + 1 != root.left.val:
        left = 1
    if root.right != None and root.val + 1 != root.right.val:
        right = 1
    cur = max(left, right)
    self.fullMax = max(self.fullMax, cur)
    return cur


# so so
def longestConsecutive(self, root):
	def dfs(node):
	    nonlocal res                           # 设置res为全局变量，以此保存最长连续序列长度
	    if not node:                           # 若节点为None，返回0，防止输入节点为空
	        return 0

	    length = 1                             # 如果节点与子节点的值不连续，那么长度为1

	    if node.left:                          # 如果存在左节点，对左节点进行深度遍历
	        l = dfs(node.left)
	        if node.left.val - node.val == 1:  # 如果节点与左节点的值连续
	            length = max(length,l+1)       # 更新当前节点node的最长连续序列长度

	    if node.right:                         # 如果存在右节点，对右节点进行深度遍历
	        r = dfs(node.right)
	        if node.right.val - node.val == 1: # 如果节点与右节点的值连续
	            length = max(length, r+1)      # 更新当前节点node的最长连续序列长度
	    res = max(res,length)                  # 更新全局的最大长度
	    return length                          # 返回当前节点node的最大长度
	res = 0                                    # 初始化res
	dfs(root)                                  # 调用dfs函数
	return res


#
def longestConsecutive(self, root: TreeNode) -> int:
    self.ans = 0
    def dfs(root):
        if not root: return 0
        l = dfs(root.left) + 1
        r = dfs(root.right) + 1
        if root.left and root.val + 1 != root.left.val:
            # 将左子树抽象想象为一个节点
            l = 1
        if root.right and root.val + 1 != root.right.val:
            # 同理，将右子树抽象想象为一个节点
            r = 1
        cur = max(l, r)
        self.ans = max(self.ans, cur)
        return cur
    dfs(root)
    return self.ans



































