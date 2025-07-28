"""
120.687. Longest Univalue Path
最长同值路径

Given a binary tree, find the length of the longest path where each node in 
the path has the same value. This path may or may not pass through the root.

The length of path between two nodes is represented by the number of edges between them.

 

Example 1:

Input:

              5
             / \
            4   5
           / \   \
          1   1   5
Output: 2

 

Example 2:

Input:

              1
             / \
            4   5
           / \   \
          4   4   5
Output: 2

 

Note: The given binary tree has not more than 10000 nodes. 
The height of the tree is not more than 1000.

"""

"""
def longestUnivaluePath(self, root: TreeNode) -> int:
    if not root: return 0
    cur = [(root, 0)]
    rmax = 0
    while cur:
        node, depth = cur.pop(0)
        rmax = max(rmax, depth)
        if node.left:
            if node.left.val == node.val:
                cur.append((node.left, depth + 1))
            else:
                cur.append((node.left, 0))
        if node.right:
            if node.right.val == node.val:
                cur.append((node.right, depth + 1))
            else:
                cur.append((node.right, 0))
    return rmax
"""



def longestUnivaluePath(self, root):
    self.ans = 0

    def arrow_length(node):
        if not node: return 0
        left_length = arrow_length(node.left)
        right_length = arrow_length(node.right)
        left_arrow = right_arrow = 0
        if node.left and node.left.val == node.val:
            left_arrow = left_length + 1
        if node.right and node.right.val == node.val:
            right_arrow = right_length + 1
        self.ans = max(self.ans, left_arrow + right_arrow)
        return max(left_arrow, right_arrow)

    arrow_length(root)
    return self.ans







def longestUnivaluePath(self, root):
    # Time: O(n)
    # Space: O(n)
    longest = [0]
    def traverse(node):
        if not node:
            return 0
        left_len, right_len = traverse(node.left), traverse(node.right)
        left = (left_len + 1) if node.left and node.left.val == node.val else 0
        right = (right_len + 1) if node.right and node.right.val == node.val else 0
        longest[0] = max(longest[0], left + right)
        return max(left, right)
    traverse(root)
    return longest[0]



def longestUnivaluePath(self, root):
    self.longest = 0
    def traverse(node, parent_val):
        if not node:
            return 0
        left, right = traverse(node.left, node.val), traverse(node.right, node.val)
        self.longest = max(self.longest, left + right)
        return 1 + max(left, right) if node.val == parent_val else 0
    traverse(root, None)
    return self.longest



def longestUnivaluePath(self, root: TreeNode) -> int:
        self.ans = 0
        def GainEqual(root):
            if not root:
                return 0
            left_length = GainEqual(root.left)
            right_length = GainEqual(root.right)
            left_tmp = right_tmp = 0
            if root.left and root.left.val == root.val:
                left_tmp = left_length + 1
            if root.right and root.right.val == root.val:
                right_tmp = right_length + 1
            self.ans = max(self.ans , left_tmp + right_tmp)
            return max(left_tmp, right_tmp)
        GainEqual(root)
        return self.ans





def longestUnivaluePath(self, root):
    postorder = [(0, root, None)]
    count = 0
    d = {None: 0}
    while postorder:
        seen, node, parent = postorder.pop()
        if node is None:
            continue
        if not seen:
            postorder.append((1, node, parent))
            postorder.append((0, node.right, node.val))
            postorder.append((0, node.left, node.val))
        else:
            if node.val == parent:
                d[node] = max(d[node.left], d[node.right]) + 1
            else:
                d[node] = 0
            count = max(count, d[node.left] + d[node.right])

    return count


def longestUnivaluePath(self, root):
    self.count = 0
    self.dfs(root)
    return self.count

def dfs(self, root):
    if root is None:
        return 0
    left = self.dfs(root.left)
    right = self.dfs(root.right)

    left = left + 1 if root.left and root.left.val == root.val else 0
    right = right + 1 if root.right and root.right.val == root.val else 0

    self.count = max(self.count, left + right)
    return max(left, right)


def longestUnivaluePath(self, root):
    def dfs(root,res):
        l,r=0,0
        if root.left:
            l=dfs(root.left,res)
            l=l+1 if root.left.val==root.val else 0
        if root.right:
            r=dfs(root.right,res)
            r=r+1 if root.right.val==root.val else 0
        res[0]=max(res[0],r+l)
        return max(l,r)
           

    if not root:
        return 0
    res=[0]
    dfs(root,res)
    return res[0]


def longestUnivaluePath(self, root):
    def dfs(root):
        if not root:
            return 0, 0
        l1, l2 = dfs(root.left)
        r1, r2 = dfs(root.right)        
        l2 = 1 + l2 if root.left and root.left.val == root.val else 0
        r2 = 1 + r2 if root.right and root.right.val == root.val else 0
        return max(l1, r1, l2 + r2), max(l2, r2)
    return dfs(root)[0]



def longestUnivaluePath(self, root):
    def dfs(node, prev_val):
        if node is None:
            return 0
        left=dfs(node.left, node.val)
        right=dfs(node.right, node.val)
        self.max_val=max(self.max_val, left+right)
        if node.val==prev_val:
            return max(left, right)+1
        return 0
    self.max_val=0
    if root is None:
        return 0
    dfs(root,root.val)
    return self.max_val



def longestUnivaluePath(self, root: TreeNode) -> int:
    # keep track of longest univalue path
    longest_uni_path = 0   
    def helper( node):
        if not node:
            return 0
        else:
            path_of_left = helper( node.left )
            path_of_right = helper( node.right )
            # if left node has the same value, extend uni path
            left_uni = path_of_left+1 if node.left and node.left.val == node.val else 0
            # if right node has the same value, extend uni path
            right_uni = path_of_right+1 if node.right and node.right.val == node.val else 0
            nonlocal longest_uni_path
            # use node as bridge to make uni_path as long as possible
            longest_uni_path = max( longest_uni_path, left_uni + right_uni )
            return max(left_uni, right_uni)                
    helper( root )
    return longest_uni_path






def longestUnivaluePath(self, root):
    self.res = 0
    self.dfs(root)
    return self.res

def dfs(self, node):
    if not node:
        return node
    left = self.dfs(node.left)
    right = self.dfs(node.right)
    left_arrow = right_arrow = 0    #初始化为0， 如果值不等，就为0.
    if node.left and node.left.val == node.val:
        left_arrow = left + 1
    if node.right and node.right.val == node.val:
        right_arrow = right + 1
    self.res = max(self.res, left_arrow + right_arrow)  #找出最大值
    return max(left_arrow, right_arrow)                 #返回左右最大值



def __init__(self):
        self.res =0 
def longestUnivaluePath(self, root: TreeNode) -> int:
    
    def maxLen(node):
        if node == None:
            return 0
        left = maxLen(node.left)
        right = maxLen(node.right)
        if node.left:
            left = left + 1 if node.left.val == node.val else 0
        if node.right:
            right = right + 1 if node.right.val == node.val else 0

        self.res = max(self.res, left+right)
        return max(left, right)
    maxLen(root)
    return self.res




def helper(self,root,preVal):
    if root is None:
        return 0
    if root.val == preVal:
        l = self.helper(root.left,root.val)
        r = self.helper(root.right,root.val)
        if l + r > self.max:
            self.max = l + r
        return max(l,r) + 1
    else:
        self.helper(root,root.val)
        return 0
def longestUnivaluePath(self, root):
    """
    :type root: TreeNode
    :rtype: int
    """
    if root is None:
        return 0
    else:
        self.helper(root,root.val)
        return self.max



def longestUnivaluePath(self, root: TreeNode) -> int:
    if not root:
        return 0
    ans = 0
    def dfs(root, s):
        nonlocal ans
        left, right = 0, 0
        if root.left:
            left = max(dfs(root.left, root.val))
            # print(left)
        if root.right:
            right = max(dfs(root.right, root.val))
            # print(right)
        ans = max(ans, left+right)
        # print(ans)
        if root.val != s:
            return [0, 0]
        else:
            return [left+1, right+1]

    left, right = 0, 0
    if root.left:
        left = max(dfs(root.left, root.val))
    if root.right:
        right = max(dfs(root.right, root.val))
    ans = max(ans, left+right)
    return ans




























