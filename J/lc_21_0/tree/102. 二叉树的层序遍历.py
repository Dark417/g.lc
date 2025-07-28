"""
102. Binary Tree Level Order Traversal

Given a binary tree, return the level order traversal of its nodes' values. (ie, from left to right, level by level).

For example:
Given binary tree [3,9,20,null,null,15,7],
    3
   / \
  9  20
    /  \
   15   7
return its level order traversal as:
[
  [3],
  [9,20],
  [15,7]
]

"""

def levelOrder(self, root):
    ans, level = [], [root]
    while root and level:
        ans.append([node.val for node in level])            
        level = [kid for n in level for kid in (n.left, n.right) if kid]
    return ans


def levelOrder(self, root: TreeNode) -> List[List[int]]:
    if not root: return []
    cur = [root]
    nl = []
    l = []
    ret = []
    while cur:
        for n in range(len(cur)):
            node = cur.pop(0)
            l.append(node.val)
            if node.left:
                nl.append(node.left)
            if node.right:
                nl.append(node.right)
        ret.append(l)
        l = []
        cur = nl
    return ret


def levelOrder(self, root: TreeNode) -> List[List[int]]:
    if not root: return []
    cur = [root]
    ret = []
    while cur:
    	l = []
    	n = len(cur)
        for _ in range(n):
            node = cur.pop(0)
            l.append(node.val)
            if node.left:
                cur.append(node.left)
            if node.right:
                cur.append(node.right)
        ret.append(l)
    return ret


def levelOrder(self, root: TreeNode) -> List[List[int]]:
    if not root: return []
    res = []
    cur_level = [root]
    while cur_level:
        tmp = []
        next_level = []
        for node in cur_level:
            tmp.append(node.val)
            if node.left:
                next_level.append(node.left)
            if node.right:
                next_level.append(node.right)
        res.append(tmp)
        cur_level = next_level
    return res



def levelOrder(self, root: TreeNode) -> List[List[int]]:
    res = []
    
    def helper(root, depth):
        if not root: return 
        if len(res) == depth:
            res.append([])
        res[depth].append(root.val)
        helper(root.left, depth + 1)
        helper(root.right, depth + 1)
    helper(root, 0)
    return res



def levelOrder(self, root):
    ans, level = [], [root]
    while root and level:
        ans.append([node.val for node in level])
        LRpair = [(node.left, node.right) for node in level]
        level = [leaf for LR in LRpair for leaf in LR if leaf]
    return ans




def levelOrder(self, root):
    if not root:
        return []
    ans, level = [], [root]
    while level:
        ans.append([node.val for node in level])
        temp = []
        for node in level:
            temp.extend([node.left, node.right])
        level = [leaf for leaf in temp if leaf]
    return ans
























