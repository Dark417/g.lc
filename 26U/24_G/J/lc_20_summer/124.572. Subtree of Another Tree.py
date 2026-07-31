"""
11.572. Subtree of Another Tree
另一个树的子树

Given two non-empty binary trees s and t, check whether tree t has exactly the same structure 
and node values with a subtree of s. A subtree of s is a tree consists of a node 
n s and all of this node's descendants. The tree s could also be considered as a subtree of itself.

Example 1:
Given tree s:

     3
    / \
   4   5
  / \
 1   2
Given tree t:
   4 
  / \
 1   2
Return true, because t has the same structure and node values with a subtree of s.
 

Example 2:
Given tree s:

     3
    / \
   4   5
  / \
 1   2
    /
   0
Given tree t:
   4
  / \
 1   2
Return false.


"""

# D Raw
def sametree(s, t):
    if not s and not t: return True
    res = 0
    if s is not None and t is not None:
        curs = [s]
        curt = [t]
        while curs:
            s1 = curs.pop(0)
            t1 = curt.pop(0)
            if s1 and t1 and s1.val == t1.val:
                curs.append(s1.left)
                curs.append(s1.right)
                curt.append(t1.left)
                curt.append(t1.right)
            else:
                return false                        
    return res

	def dfs(node):
	    res = sametree(node, t)
	    if node.left:
	        res = res or dfs(node.left, t)
	    if node.right:
	        res = res or dfs(node.right, t)
	    return res
	return dfs(s)


"""
时间复杂度：对于每一个 ss 上的点，都需要做一次 DFS 来和 tt 匹配，匹配一次的时间代价是 O(|t|)O(∣t∣)，那么总的时间代价就是 O(|s| \times |t|)O(∣s∣×∣t∣)。故渐进时间复杂度为 O(|s| \times |t|)O(∣s∣×∣t∣)。
空间复杂度：假设 ss 深度为 d_sd 
O

"""
def isSubtree(self, s: TreeNode, t: TreeNode) -> bool:
	if s == None: return False
	return check(s, t) or self.isSubtree(s.left, t) or self.isSubtree(s.right, t)

	def check(s, t):
		if not s and not t: return True
		if not s or not t: return False
		if s.val == t.val:
			return check(s.left, t.left) and check(s.right, t.right)
		return False

		return s.val == t.val amd check(s.left, t.left) and check(s.right, t.right)



def isMatch(self, s, t):
    if not(s and t):
        return s is t
    return (s.val == t.val and 
            self.isMatch(s.left, t.left) and 
            self.isMatch(s.right, t.right))

def isSubtree(self, s, t):
    if self.isMatch(s, t): return True
    if not s: return False
    return self.isSubtree(s.left, t) or self.isSubtree(s.right, t)


def isSubtree(self, s, t):
    def convert(p):
        return "^" + str(p.val) + "#" + convert(p.left) + convert(p.right) if p else "$"
    
    return convert(t) in convert(s)
























































