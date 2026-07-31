"""
103.21. Merge Two Sorted Lists
合并两个有序链表
剑指 Offer 25. 合并两个排序的链表

Merge two sorted linked lists and return it as a new sorted list. 
The new list should be made by splicing together the nodes of the first two lists.

Example:

Input: 1->2->4, 1->3->4
Output: 1->1->2->3->4->4


"""

def mergeTwoLists(self, l1, l2):
    if l1 is None:
        return l2
    elif l2 is None:
        return l1
    elif l1.val < l2.val:
        l1.next = self.mergeTwoLists(l1.next, l2)
        return l1
    else:
        l2.next = self.mergeTwoLists(l1, l2.next)
        return l2



def mergeTwoLists(self, l1, l2):
    prehead = ListNode(-1)
    prev = prehead
    while l1 and l2:
        if l1.val <= l2.val:
            prev.next = l1
            l1 = l1.next
        else:
            prev.next = l2
            l2 = l2.next            
        prev = prev.next

    prev.next = l1 if l1 is not None else l2
    return prehead.next





# D
def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
    if not l1 and not l2: return None
    if not l1 and l2: return l2
    if l1 and not l2: return l1

    cur = ListNode(0)
    res = cur
    while l1 and l2:
        if l1.val <= l2.val:
            cur.next = l1
            cur = cur.next
            l1 = l1.next
        else:
            cur.next = l2
            cur = cur.next
            l2 = l2.next
    if l1:
        cur.next = l1
        cur = cur.next
    if l2:
        cur.next = l2
        cur = cur.next
    return res.next



# Stefan
def mergeTwoLists(self, a, b):
    if a and b:
        if a.val > b.val:N
            a, b = b, a
        a.next = self.mergeTwoLists(a.next, b)
    return a or b


def mergeTwoLists(self, a, b):
    if not a or b and a.val > b.val:
        a, b = b, a
    if a:
        a.next = self.mergeTwoLists(a.next, b)
    return a


# official
def mergeTwoLists(self, l1, l2):
    if l1 is None:
        return l2
    elif l2 is None:
        return l1
    elif l1.val < l2.val:
        l1.next = self.mergeTwoLists(l1.next, l2)
        return l1
    else:
        l2.next = self.mergeTwoLists(l1, l2.next)
        return l2


def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
    if not l1: return l2  # 终止条件，直到两个链表都空
    if not l2: return l1
    if l1.val <= l2.val:  # 递归调用
        l1.next = self.mergeTwoLists(l1.next,l2)
        return l1
    else:
        l2.next = self.mergeTwoLists(l1,l2.next)
        return l2


# caikehe
# iteratively
def mergeTwoLists1(self, l1, l2):
    dummy = cur = ListNode(0)
    while l1 and l2:
        if l1.val < l2.val:
            cur.next = l1
            l1 = l1.next
        else:
            cur.next = l2
            l2 = l2.next
        cur = cur.next
    cur.next = l1 or l2
    return dummy.next
    
# recursively    
def mergeTwoLists2(self, l1, l2):
    if not l1 or not l2:
        return l1 or l2
    if l1.val < l2.val:
        l1.next = self.mergeTwoLists(l1.next, l2)
        return l1
    else:
        l2.next = self.mergeTwoLists(l1, l2.next)
        return l2
        
# in-place, iteratively        
def mergeTwoLists(self, l1, l2):
    if None in (l1, l2):
        return l1 or l2
    dummy = cur = ListNode(0)
    dummy.next = l1
    while l1 and l2:
        if l1.val < l2.val:
            l1 = l1.next
        else:
            nxt = cur.next
            cur.next = l2
            tmp = l2.next
            l2.next = nxt
            l2 = tmp
        cur = cur.next
    cur.next = l1 or l2
    return dummy.next



# commnent
# solution 1
def mergeTwoLists(self, l1, l2):
    if l1 is None or (l2 and l1.val>l2.val):
        l1, l2 = l2, l1
    tail = l1
    while tail and l2:
        if tail.next is None or (tail.next.val > l2.val):
            tail.next, l2 = l2, tail.next
        tail = tail.next
    return l1    
# solution 2, same as OP's solution 1
def mergeTwoLists1(self, l1, l2):
    head = tail = ListNode(0)
    while l1 and l2:
        if l1.val<=l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 if l1 else l2 # a better way is tail.next = l1 or l2, as in OP's code
    return head.next



def mergeTwoLists(self, l1, l2):
    if None in (l1, l2):
        return l1 or l2
    dummy = cur = ListNode(0)
    while l1 and l2:
        cur.next = l1
        if l1.val < l2.val:
            l1 = l1.next
        else:
            tmp = l2.next
            cur.next = l2
            l2.next = l1
            l2 = tmp
        cur = cur.next
    cur.next = l1 or l2
    return dummy.next 

def mergeTwoLists(self, l1, l2):
	dummy = cur = ListNode(0)
	while l1 and l2:
	cur.next = l1
	if l1.val < l2.val:
	l1 = l1.next
	else:
	cur.next = l2
	l2 = l2.next
	cur = cur.next
	cur.next = l1 or l2
	return dummy.next



















