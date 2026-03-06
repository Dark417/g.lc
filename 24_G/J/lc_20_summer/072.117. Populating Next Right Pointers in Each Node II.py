"""
072.117. Populating Next Right Pointers in Each Node II
填充每个节点的下一个右侧节点指针 II


Given a binary tree

struct Node {
  int val;
  Node *left;
  Node *right;
  Node *next;
}
Populate each next pointer to point to its next right node. If there is no next right 
node, the next pointer should be set to NULL.

Initially, all next pointers are set to NULL.

Follow up:

You may only use constant extra space.
Recursive approach is fine, you may assume implicit stack space does not count as extra space for this problem.
 

Example 1:

Input: root = [1,2,3,4,5,null,7]
Output: [1,#,2,3,#,4,5,7,#]
Explanation: Given the above binary tree (Figure A), your function should populate each next pointer to point 
to its next right node, just like in Figure B. The serialized output is in level order as connected by 
the next pointers, with '#' signifying the end of each level.
 

Constraints:

The number of nodes in the given tree is less than 6000.
-100 <= node.val <= 100

leftmost = root
while (leftmost != null)
{
    curr = leftmost
    prev = NULL
    while (curr != null)
    {
        → process left child
        → process right child
        → set leftmost for the next level
        curr = curr.next
    }
}




"""

# D

#

def connect(self, root: 'Node') -> 'Node':

	return root





# official
def processChild(self, childNode, prev, leftmost):
    if childNode:
        
        # If the "prev" pointer is alread set i.e. if we
        # already found atleast one node on the next level,
        # setup its next pointer
        if prev:
            prev.next = childNode
        else:    
            # Else it means this child node is the first node
            # we have encountered on the next level, so, we
            # set the leftmost pointer
            leftmost = childNode
        prev = childNode 
    return prev, leftmost
    
def connect(self, root: 'Node') -> 'Node':
    
    if not root:
        return root
    
    # The root node is the only node on the first level
    # and hence its the leftmost node for that level
    leftmost = root
    
    # We have no idea about the structure of the tree,
    # so, we keep going until we do find the last level.
    # The nodes on the last level won't have any children
    while leftmost:
        
        # "prev" tracks the latest node on the "next" level
        # while "curr" tracks the latest node on the current
        # level.
        prev, curr = None, leftmost
        
        # We reset this so that we can re-assign it to the leftmost
        # node of the next level. Also, if there isn't one, this
        # would help break us out of the outermost loop.
        leftmost = None
        
        # Iterate on the nodes in the current level using
        # the next pointers already established.
        while curr:
            
            # Process both the children and update the prev
            # and leftmost pointers as necessary.
            prev, leftmost = self.processChild(curr.left, prev, leftmost)
            prev, leftmost = self.processChild(curr.right, prev, leftmost)
            
            # Move onto the next node.
            curr = curr.next
            
    return root 












# dis

def connect(self, root):
    prekid = kid = TreeLinkNode(0)
    while root:
        while root:
            kid.next = root.left
            kid = kid.next or kid
            kid.next = root.right
            kid = kid.next or kid
            root = root.next
        root, kid = prekid.next, prekid


def connect(self, root):
	old_root = root
	prekid = Node(0)
	kid = prekid   # Let kid point to prekid 
	while root:
	    while root:
	        if root.left:
	            kid.next = root.left
	            kid = kid.next
	        if root.right:
	            kid.next = root.right
	            kid = kid.next
	        root = root.next
	    root, kid = prekid.next, prekid
	    kid.next = None  # Reset the chain for prekid
	return old_root


def connect(self, node):
    tail = dummy = TreeLinkNode(0)
    while node:
        tail.next = node.left
        if tail.next:
            tail = tail.next
        tail.next = node.right
        if tail.next:
            tail = tail.next
        node = node.next
        if not node:
            tail = dummy
            node = dummy.next


def connect(self, root):
    while root:
        cur = tmp = TreeLinkNode(0)
        while root:
            if root.left:
                cur.next = root.left
                cur = root.left
            if root.right:
                cur.next = root.right
                cur = root.right
            root = root.next
        root = tmp.next


def connect(self, node):
    head = tail = TreeLinkNode(0)
    while node:
        for c in (node.left, node.right):
            tail.next = c
            if c:
                tail = tail.next
        if node.next:
            node = node.next
        else:
            node, tail = head.next, head 


def connect(self, root):
	while root:
		node = tem = TreeLinkNode(0)
		while root:
		    if root.left: node.next = node = root.left
		    if root.right: node.next = node = root.right
		    root = root.next
		root = tem.next


def connect(self, root):
    if not root:
        return

    sentinel = rear = TreeLinkNode(0)
    # enqueue root
    front = root
    front.next = rear

    while front is not rear:
        # dequeue from front
        node  = front
        front = front.next
        # if sentinel is dequeued
        if node is sentinel:
            # if rear has non sentinel items
            # enqueue sentinel back
            if rear is not sentinel:
                rear.next = sentinel
                rear = rear.next
                continue

        if node.next is sentinel: # full level is traversed
            node.next = None

        # enqueue left
        if node.left:
            rear.next = node.left
            rear = rear.next
        # enqueue right
        if node.right:
            rear.next = node.right
            rear = rear.next



def connect(self, root: 'Node') -> 'Node':
	if not root:
        return root
    q = []
    
    q.append(root)
    
    tail = root
    while len(q) > 0:
        node = q.pop(0)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
            
        if node == tail:
            node.next = None
            tail = q[-1] if len(q) > 0 else None
        else:
            node.next = q[0]
            
    return root


def connect(self, root: 'Node') -> 'Node':
    dummy = Node(-1, None, None, None)
    tmp = dummy
    res = root
    while root:
        while root:
            if root.left:
                tmp.next = root.left
                tmp = tmp.next
            if root.right:
                tmp.next = root.right
                tmp = tmp.next
            root = root.next
        root = dummy.next
        tmp = dummy
        dummy.next = None
        
    return res

















