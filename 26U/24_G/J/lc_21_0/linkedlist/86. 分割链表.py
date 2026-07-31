# 86. 分割链表

def partition(self, head: ListNode, x: int) -> ListNode:
    sent = pre1 = ListNode(-1)
    sent2 = pre2 = ListNode(-2)

    cur = head
    while cur:
        if cur.val < x:
            pre1.next = cur
            pre1 = pre1.next
        if cur.val >= x:
            pre2.next = cur
            pre2 = pre2.next
        cur = cur.next
    pre1.next = sent2.next
    pre2.next = None
    return sent.next
































