"""
125.100. Same Tree
相同的树

Given two binary trees, write a function to check if they are the same or not.

Two binary trees are considered the same if they are structurally identical and the nodes have the same value.

Example 1:

Input:     1         1
          / \       / \
         2   3     2   3

        [1,2,3],   [1,2,3]

Output: true
Example 2:

Input:     1         1
          /           \
         2             2

        [1,2],     [1,null,2]

Output: false
Example 3:

Input:     1         1
          / \       / \
         2   1     1   2

        [1,2,1],   [1,1,2]

Output: false

"""

def isSameTree(self, p: TreeNode, q: TreeNode) -> bool:
    def check(p, q):
        if not p and not q: return True
        if p and q:
            if p.val == q.val:
                return check(p.left, q.left) and check(p.right, q.right)
        return False
    return check(p, q)


def isSameTree(self, p: TreeNode, q: TreeNode) -> bool:
    if not p and not q: return True
    if p and q:
        if p.val == q.val:
            return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
    return False


def isSubtree(self, s: TreeNode, t: TreeNode) -> bool:
    if not s: 
        return False
    if self.isSameTree(s, t): 
        return True
    return self.isSubtree(s.left, t) or self.isSubtree(s.right, t)

def isSameTree(self, p: TreeNode, q: TreeNode) -> bool:
    if p and q:
        return p.val == q.val and self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
    return p is q


def isSubtree(self, s, t):
    def check(s, t):
        # helper function that does the actual subtree check
        if (s is None) and (t is None):
            return True
        if (s is None) or (t is None):
            return False
        return (s.val == t.val and check(s.left, t.left) and check(s.right, t.right))

    # need to do a pre-order traversal and do a check
    # for every node we visit for the subtree
    if not s:
        # return False since None cannot contain a subtree 
        return
    if check(s, t):
        # we found a match
        return True
    if self.isSubtree(s.left, t) or self.isSubtree(s.right, t):
        # a match was found
        return True
    return False



def isSameTree(self, p, q):
    def check(p, q):
        # if both are None
        if not p and not q:
            return True
        # one of p and q is None
        if not q or not p:
            return False
        if p.val != q.val:
            return False
        return True
    
    deq = deque([(p, q),])
    while deq:
        p, q = deq.popleft()
        if not check(p, q):
            return False
        
        if p:
            deq.append((p.left, q.left))
            deq.append((p.right, q.right))
                
    return True


def isSameTree(self, p, q):
    def check(p, q):
        # if both are None
        if not p and not q:
            return True
        # one of p and q is None
        if not q or not p:
            return False
        if p.val != q.val:
            return False
        return True
    
    deq = deque([(p, q),])
    while deq:
        p, q = deq.popleft()
        if not check(p, q):
            return False




"""
Naive approach, O(|s| * |t|)
For each node of s, let's check if it's subtree equals t. 
We can do that in a straightforward way by an isMatch function: check if s and t 
match at the values of their roots, plus their subtrees match. Then, in our main 
function, we want to check if s and t match, or if t is a subtree of a child of s.
"""
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




"""
Advanced approach, O(|s| + |t|) (Merkle hashing):
For each node in a tree, we can create node.merkle, a hash representing it's subtree.
This hash is formed by hashing the concatenation of the merkle of the left child, 
the node's value, and the merkle of the right child. Then, two trees are identical if 
and only if the merkle hash of their roots are equal (except when there is a hash 
collision.) From there, finding the answer is straightforward: we simply check if any node in s has node.merkle == t.merkle
"""
def isSubtree(self, s, t):
    from hashlib import sha256
    def hash_(x):
        S = sha256()
        S.update(x)
        return S.hexdigest()
        
    def merkle(node):
        if not node:
            return '#'
        m_left = merkle(node.left)
        m_right = merkle(node.right)
        node.merkle = hash_(m_left + str(node.val) + m_right)
        return node.merkle
        
    merkle(s)
    merkle(t)
    def dfs(node):
        if not node:
            return False
        return (node.merkle == t.merkle or 
                dfs(node.left) or dfs(node.right))
                    
    return dfs(s)




def isSubtree(self, s: TreeNode, t: TreeNode) -> bool:
    string_s = self.traverse_tree(s)
    string_t = self.traverse_tree(t)
    if string_t in string_s:
        return True
    return False



def traverse_tree(self, s):
    if s:
        return f"#{s.val} {self.traverse_tree(s.left)} {self.traverse_tree(s.right)}"
    return None


def isSubtree(self, s: TreeNode, t: TreeNode) -> bool:
    def traverse_tree(node):
        if not node: return None
        return f"#{node.val} {traverse_tree(node.left)} {traverse_tree(node.right)}"
    return traverse_tree(t) in traverse_tree(s)







































































