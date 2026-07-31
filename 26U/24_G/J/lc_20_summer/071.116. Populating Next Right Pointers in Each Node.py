"""
071.116. Populating Next Right Pointers in Each Node
填充每个节点的下一个右侧节点指针


You are given a perfect binary tree where all leaves are on the same level, and every parent has two children. The binary tree has the following definition:

struct Node {
  int val;
  Node *left;
  Node *right;
  Node *next;
}
Populate each next pointer to point to its next right node. If there is no next right node, the next pointer should be set to NULL.

Initially, all next pointers are set to NULL.

 

Follow up:

You may only use constant extra space.
Recursive approach is fine, you may assume implicit stack space does not count as extra space for this problem.
 

Example 1:



Input: root = [1,2,3,4,5,6,7]
Output: [1,#,2,3,#,4,5,6,7,#]
Explanation: Given the above perfect binary tree (Figure A), your function should populate each next pointer to point to its next right node, just like in Figure B. The serialized output is in level order as connected by the next pointers, with '#' signifying the end of each level.
 

Constraints:

The number of nodes in the given tree is less than 4096.
-1000 <= node.val <= 1000


""" 


# D
# bfs
def connect(self, root: 'Node') -> 'Node':
    if not root: return None
    cur = [root]
    lnext = []
    ll = [[root]]
    while cur:
        for node in cur:
            if node.left:
                lnext.append(node.left)
            if node.right:
                lnext.append(node.right)
        ll.append(lnext)
        cur = lnext
        lnext = []
    for l in ll:
        for i in range(len(l)-1):
            l[i].next = l[i+1]
    #l[-1].next = NULL
    return root

def connect(self, root: 'Node') -> 'Node':
	if not root: return None
	ll = []

	def dfs(root, level)
		if root:
			if len(ll) = level:
				ll.append([])
			ll[level].append(root)
			if node.left:
				dfs(root.left, level+1)
			if node.right:
				dfs(root.right, level+1)

	dfs(root, 0)
	for l in ll:
        for i in range(len(l)-1):
            l[i].next = l[i+1]
    #l[-1].next = NULL
    return root


# Stefan
def connect(self, root):
    while root and root.left:
        next = root.left
        while root:
            root.left.next = root.right
            root.right.next = root.next and root.next.left
            root = root.next
        root = next

    Q = root
    while root and root.left:
      next = root.left 
      while root:
          root.left.next = root.right 
          root.right.next = root.next and root.next.left 
          root = root.next
      root = next
    return Q
    

# caikehe
def connect1(self, root):
    if root and root.left and root.right:
        root.left.next = root.right
        if root.next:
            root.right.next = root.next.left
        self.connect(root.left)
        self.connect(root.right)


def connect2(self, root):
    if not root:
        return 
    queue = [root]
    while queue:
        curr = queue.pop(0)
        if curr.left and curr.right:
            curr.left.next = curr.right
            if curr.next:
                curr.right.next = curr.next.left
            queue.append(curr.left)
            queue.append(curr.right)


def connect(self, root):
    if not root:
        return 
    stack = [root]
    while stack:
        curr = stack.pop()
        if curr.left and curr.right:
            curr.left.next = curr.right
            if curr.next:
                curr.right.next = curr.next.left
            stack.append(curr.right)
            stack.append(curr.left)


# official
def connect(self, root: 'Node') -> 'Node':  
    if not root:
        return root
    Q = collections.deque([root])
    while Q:
        size = len(Q)
        for i in range(size):
            node = Q.popleft()
            if i < size - 1:
                node.next = Q[0]
            if node.left:
                Q.append(node.left)
            if node.right:
                Q.append(node.right)
    return root


def connect(self, root: 'Node') -> 'Node':
    if not root: return root
    leftmost = root
    while leftmost.left:
        head = leftmost
        while head:
            head.left.next = head.right
            if head.next:
                head.right.next = head.next.left
            head = head.next
        leftmost = leftmost.left
    return root


def connect(self, root):
    if not root: return root
    while root.left:
        cur = root.left
        prev = None
        while root:
            if prev: prev.next = root.left
            root.left.next = root.right
            prev = root.right
            root = root.next
        root = cur
    return root


def connect(self, root):
    if not root: return None
    cur  = root
    next = root.left
    while cur.left:
        cur.left.next = cur.right
        if cur.next:
            cur.right.next = cur.next.left
            cur = cur.next
        else:
            cur = next
            next = cur.left
    return root



def helper(self, left, right):
    if not left or not right:
        return
    left.next = right
    self.helper(left.right, right.left)
    self.helper(left.left, left.right)
    self.helper(right.left, right.right)

def connect(self, root):
    if not root:
        return
    self.helper(root.left, root.right)


# half way
def dfs(node, next):
    if node:
        dfs(node.left, node.right)
        dfs(node.right, node.next.left if next)

def connect(self, root: 'Node') -> 'Node':
    dfs(root, None)
    return root



def connect(self, root: 'Node') -> 'Node':
    def levelOrder(root: 'Node') -> List[List['Node']]:
        if not root:
            return []
        tmp = []
        ret = []
        ret += [[root]]
        while ret[-1]:
            ret += [[]]
            for i in ret[-2][:]:
                if i.left:
                    ret[-1] += [i.left]
                    if i.right:
                        tmp += [i.right]
                        ret[-1] += [i.right]
                elif i.right:
                    tmp += [i.right]
                    ret[-1] += [i.right]
        return ret[:-1]
    
    def fillnext(next_lst: List['Node'], root: 'Node', x: int, y: int):
        if not root:
            return
        root.next = next_lst[2**x+y-1]
        fillnext(next_lst, root.left, x+1, y*2)
        fillnext(next_lst, root.right, x+1, y*2+1)

    next_lst = []
    for i in levelOrder(root):
        next_lst += i[1:]+[None]
    fillnext(next_lst, root, 0, 0)
    return root


































