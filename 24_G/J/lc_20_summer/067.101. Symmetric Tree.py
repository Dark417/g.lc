"""
067.101. Symmetric Tree
对称二叉树


Given a binary tree, check whether it is a mirror of itself 
(ie, symmetric around its center).

For example, this binary tree [1,2,2,3,4,4,3] is symmetric:

    1
   / \
  2   2
 / \ / \
3  4 4  3
 

But the following [1,2,2,null,3,null,3] is not:

    1
   / \
  2   2
   \   \
   3    3
 

Follow up: Solve it both recursively and iteratively.


"""

def isSymmetric(self, root: TreeNode) -> bool:
    if not root: return True
    def left(node, l):
        if not root: [None]
        ret = [node]
        cur = deque()
        cur.append(node)
        final = []
        while cur:
            n = cur.popleft()
            if not n:
                ret.append(None)
                continue
            if l == 1:
                cur.append(n.left)
                cur.append(n.right)
                ret += [n.left, n.right]
            else:
                cur.append(n.right)
                cur.append(n.left)
                ret += [n.right, n.left]
        for i in ret:
            if i:
                final.append(i.val)
            else:
                final.append(None)
        return final
    return left(root.left, 1) == left(root.right, 0)




def isSymmetric(self, root: TreeNode) -> bool:
	def check(p, q):
		if not p and not q: return True
		if not p or not q: return False
		return p.val == q.val and check(p.left, q.right) and check(p.right, q.left)
	return check(root, root)


# lee
def isSymmetric(self, root):
    def isSym(L,R):
        if L and R and L.val == R.val: 
            return isSym(L.left, R.right) and isSym(L.right, R.left)
        return L == R
    return not root or isSym(root.left, root.right)


def isSymmetric(self, root):
    queue = [root]
    while queue:
        values = [i.val if i else None for i in queue]
        if values != values[::-1]: return False
        queue = [child for i in queue if i for child in (i.left, i.right)]
    return True



def isSymmetric(self, root):
    if not root:
        return True
    return self.dfs(root.left, root.right)
    
def dfs(self, l, r):
    if l and r:
        return l.val == r.val and self.dfs(l.left, r.right) and self.dfs(l.right, r.left)
    return l == r
    
# simplify conditionals


#
if not root or not (root.left or root.right):
	return True

#
def isSymmetric(self, root: TreeNode) -> bool:
	def check(u, v):
		q = deque()
		q.append(u)
		q.append(v)
		while q:
			u = q.popleft()
			v = q.popleft()
			if not u and not v: continue
            if not u or not v: return False
            if u.val != v.val: return False
			q.append(u.left)
			q.append(v.right)

			q.append(u.right)
			q.append(v.left)

	return check(root, root)



#
def isSymmetric(self, root: TreeNode) -> bool:
    if not root: return True

def check(a):
    half = len(a) // 2
    for i in range(half):
        if a[i] != a[~i]:
            return False
    return True

from collections import deque
q = deque([root])
while q:
    t = []
    for i in range(len(q)):
        node = q.popleft()
        if node:
            t.append(node.val)
            q.extend([node.left, node.right])
        else:
            t.append("")       #<-----------
    if not check(t): return False
return True


# """迭代法"""
def isSymmetric(self, root: TreeNode) -> bool: 
    if not root: return True
    queue = [(root.left, root.right)]
    while queue:
        node1, node2 = queue.pop(0)
        if not node1 and not node2:  # 都为None
            continue
        elif node1 and node2:  # 都不为None
            if not node1.val == node2.val:  # 值不相等
                return False
            queue += [(node1.left, node2.right), (node1.right, node2.left)]
        else:
            return False
    return True


class Solution {
    LinkedList<TreeNode> inorder = new LinkedList<>();
    public boolean isSymmetric(TreeNode root) {
        inorder(root, 1);
        while (inorder.size()>1) {
            if (inorder.pollFirst().val != inorder.pollLast().val){
                return false;
            }
        }
        return true;
    }
    private void inorder(TreeNode node, int level){
        if (node == null) {
            inorder.addLast(new TreeNode(-level));
            return;
        }
        level++;
        inorder(node.left, level);
        inorder.addLast(node);
        inorder(node.right, level);
    }
}











