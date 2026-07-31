# 369. 给单链表加一


def plusOne(self, head: ListNode) -> ListNode:
    x = 0
    while head:
        x = x * 10 + head.val
        head = head.next
    z = list(int(i) for i in str(x+1))
    pre = cur = ListNode(None)
    for i in z:
        cur.next = ListNode(i)
        cur = cur.next
    return pre.next


































