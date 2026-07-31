"""
116.203. Remove Linked List Elements
移除链表元素

Remove all elements from a linked list of integers that have value val.

Example:

Input:  1->2->6->3->4->5->6, val = 6
Output: 1->2->3->4->5

"""
def removeElements(self, head: ListNode, val: int) -> ListNode:
    if not head:
        return None
    head.next = self.removeElements(head.next, val)
    if head.val == val:
        return head.next
    else:
        return head
            
def removeElements(self, head: ListNode, val: int) -> ListNode:
    sentinel = ListNode(0)
    sentinel.next = head
    
    prev, curr = sentinel, head
    while curr:
        if curr.val == val:
            prev.next = curr.next
        else:
            prev = curr
        curr = curr.nex
    return sentinel.next



def removeElements(self, head: ListNode, val: int) -> ListNode:
    while head and head.val == val:
        head = head.next
    if not head:
        return head
    pre = head
    while pre.next:
        if pre.next.val == val:
            pre.next = pre.next.next
        else:
            pre = pre.next
    return head



def deleteNode(self, head: ListNode, val: int) -> ListNode:
    dummy = ListNode(0)  # 设置伪结点
    dummy.next = head
    if head.val == val: return head.next # 头结点是要删除的点，直接返回
    while head and head.next:
        if head.next.val == val:   # 找到了要删除的结点，删除
            head.next = head.next.next
        head = head.next
    return dummy.next


def deleteNode(self, head, val):
    if head is None or val is None:
        return None
    if val.next is not None:  # 待删除节点不是尾节点
        tmp = val.next
        val.val = tmp.val
        val.next = tmp.next
    elif head == val:  # 待删除节点只有一个节点，此节点为头节点
        head = None
    else:
        cur = head    # 待删除节点为尾节点
        while cur.next != val:
            cur = cur.next
        cur.next = None
    return head







def removeElements(self, head: ListNode, val: int) -> ListNode:
    cur = head
    start = pre = ListNode(0)
    pre.next = head
    while cur:
        if cur.val == val:
            cur = cur.next		# because thought return pre, so this order
            pre.next = cur 		# if start / sentinel, can mess with this like next
        else:
            pre = cur
            cur = cur.next
    return start.next


def removeElements(self, head, val):
    dummy = ListNode(-1)
    dummy.next = head
    next = dummy
    while next != None and next.next != None:
        if next.next.val == val:
            next.next = next.next.next
        else:
            next = next.next
    return dummy.next






"""
No sentinel
public ListNode removeElements(ListNode head, int val)
    {
        while (head != null && head.val == val)
            head = head.next;
        ListNode prev = head;
        if (prev != null)
        {
            while (prev.next != null)
            {
                if (prev.next.val == val)
                    prev.next = prev.next.next;
                else
                    prev = prev.next;
            }
        }
        return head;
    }
"""
































