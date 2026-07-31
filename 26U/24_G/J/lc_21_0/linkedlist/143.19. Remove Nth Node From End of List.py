"""
143.19. Remove Nth Node From End of List
删除链表的倒数第 N 个结点


Given a linked list, remove the n-th node from the end of list and return its head.

Example:

Given linked list: 1->2->3->4->5, and n = 2.

After removing the second node from the end, the linked list becomes 1->2->3->5.
Note:

Given n will always be valid.

Follow up:

Could you do this in one pass?

"""

dummy = ListNode(0, head)



def removeNthFromEnd(self, head, n):
    dummy = ListNode(0)
    dummy.next = head
    fast = slow = dummy
    for _ in xrange(n):
        fast = fast.next
    while fast and fast.next:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next


def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
    sent = pre = ListNode(None)
    sent.next = cur = head
    for _ in range(n):
        cur = cur.next
    while cur:
        pre = pre.next
        cur = cur.next
    pre.next = pre.next.next
    return sent.next


def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
    sent = pre = ListNode(None)
    sent.next = cur = head
    for _ in range(n-1):
        cur = cur.next
    while cur.next:
        pre = pre.next
        cur = cur.next
    pre.next = pre.next.next
    return sent.next



def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
    pre = s = ListNode(0)
    pre.next = head
    end = head
    while n-1:
        end = end.next
        n -= 1
    while end.next:
        s = s.next
        end = end.next
    if s.next:
        s.next = s.next.next
    return pre.next


def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
    pre = s = ListNode(0)
    pre.next = head
    cur = head
    l = 0
    while cur:
        cur = cur.next
        l += 1
    k = l - n
    for _ in range(k):
        s = s.next
    s.next = s.next.next
    return pre.next


def removeNthFromEnd(self, head, n):
    def index(node):
        if not node:
            return 0
        i = index(node.next) + 1
        if i > n:
            node.next.val = node.val
        return i
    index(head)
    return head.next



def removeNthFromEnd(self, head, n):
    def remove(head):
        if not head:
            return 0, head
        i, head.next = remove(head.next)
        return i+1, (head, head.next)[i+1 == n]
    return remove(head)[1]




def removeNthFromEnd(self, head, n):
    slow = fast = self
    self.next = head
    while fast.next:
        if n:
            n -= 1
        else:
            slow = slow.next
        fast = fast.next
    slow.next = slow.next.next
    return self.next   


def removeNthFromEnd(self, head, n):
    self.next, nodelist  = head, [self]
    while head.next:
        if len(nodelist) == n:
            nodelist.pop(0)
        nodelist += head,
        head = head.next
    nodelist[0].next = nodelist[0].next.next 
    return self.next






















