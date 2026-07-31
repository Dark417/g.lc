# 328. 奇偶链表

def oddEvenList(self, head: ListNode) -> ListNode:
    if not head:
        return head
    pre = even = ListNode(None)
    cur = head
    while cur and cur.next:
        even.next = cur.next
        even = even.next
        cur.next = cur.next.next
        if cur.next:
            cur = cur.next
    even.next = None
    cur.next = pre.next
    return head


def oddEvenList(self, head: ListNode) -> ListNode:
    if not head:
        return head
    evenHead = head.next
    odd, even = head, evenHead
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = evenHead
    return head







































