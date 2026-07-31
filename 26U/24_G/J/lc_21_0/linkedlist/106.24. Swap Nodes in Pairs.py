"""
106.24. Swap Nodes in Pairs
两两交换链表中的节点


Given a linked list, swap every two adjacent nodes and return its head.

You may not modify the values in the list's nodes, only nodes itself may be changed.

 

Example:

Given 1->2->3->4, you should return the list as 2->1->4->3.

"""




# learn
def swapPairs(self, head: ListNode) -> ListNode:
	dummy = ListNode(-1)
	dummy.next = head
	pre = dummy
	while head and head.next:
		first = head
		second = head.next

		pre.next = second
		first.next = second.next
		second.next = first

		pre = first
		head = first.next
	return dummy.next



def swapPairs(self, head: ListNode) -> ListNode:
    dummyHead = ListNode(0)
    dummyHead.next = head
    temp = dummyHead
    while temp.next and temp.next.next:
        node1 = temp.next
        node2 = temp.next.next
        temp.next = node2
        node1.next = node2.next
        node2.next = node1
        temp = node1
    return dummyHead.next



# Recursively    
def swapPairs(self, head):
    if head and head.next:
        tmp = head.next
        head.next = self.swapPairs(tmp.next)
        tmp.next = head
        return tmp
    return head

# recursively    
def swapPairs(self, head):
    if not head or not head.next:
        return head
    second = head.next
    head.next = self.swapPairs(second.next)
    second.next = head
    return second

    
def swapPairs(self, head):
    if not head or not head.next: return head
    new_start = head.next.next
    head, head.next = head.next, head
    head.next.next = self.swapPairs(new_start)
    return head

# recursion
def swapPairs(self, head: ListNode) -> ListNode:
        # If the list has no node or has only one node left.
        if not head or not head.next:
            return head

        # Nodes to be swapped
        first_node = head
        second_node = head.next

        # Swapping
        first_node.next  = self.swapPairs(second_node.next)
        second_node.next = first_node

        # Now the head is the second node
        return second_node


# Stafen
def swapPairs(self, head):
    pre, pre.next = self, head
    while pre.next and pre.next.next:
        a = pre.next
        b = a.next
        pre.next, b.next, a.next = b, a, b.next
        pre = a
    return self.next

# zhou
def swapPairs(self, head):
    if not head or not head.next: return head
    dummy = ListNode(0)
    dummy.next = head
    cur = dummy
    
    while cur.next and cur.next.next:
        first = cur.next
        sec = cur.next.next
        cur.next = sec
        first.next = sec.next
        sec.next = first
        cur = cur.next.next
    return dummy.next 


# caikehe
# Iteratively
def swapPairs1(self, head):
    dummy = p = ListNode(0)
    dummy.next = head
    while head and head.next:
        tmp = head.next
        head.next = tmp.next
        tmp.next = head
        p.next = tmp
        head = head.next
        p = tmp.next
    return dummy.next




# iteratively
def swapPairs1(self, head):
    if not head or not head.next:
        return head
    second = head.next 
    pre = ListNode(0)
    while head and head.next:
        nxt = head.next
        head.next = nxt.next
        nxt.next = head
        pre.next = nxt
        head = head.next
        pre = nxt.next
    return second








def swapPairs(self, head):
    prev = self
    prev.next = head
    while prev.next and prev.next.next:
    	prev.next, prev.next.next, prev.next.next.next = prev.next.next, prev.next, prev.next.next.next
    	prev = prev.next.next
    return self.next





# D
def swapPairs(self, head: ListNode) -> ListNode:
    if not head: return head
    dummy = ListNode(0)
    dummy.next = head
    pre = dummy
    cur = head
    while cur:
        if cur.next and cur.next.next:
            nextnext = cur.next.next
            pre.next = cur.next
            cur.next.next = cur
            cur.next = nextnext
            pre = cur
            cur = nextnext
        elif cur.next:
            next = cur.next
            cur.next = None
            next.next = cur
            pre.next = next
        else:
            break
    return dummy.next











































