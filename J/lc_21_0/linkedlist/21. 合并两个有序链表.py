# 21. 合并两个有序链表


def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
    if not l1: return l2  # 终止条件，直到两个链表都空
    if not l2: return l1
    if l1.val <= l2.val:  # 递归调用
        l1.next = self.mergeTwoLists(l1.next,l2)
        return l1
    else:
        l2.next = self.mergeTwoLists(l1,l2.next)
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

    # 合并后 l1 和 l2 最多只有一个还未被合并完，我们直接将链表末尾指向未合并完的链表即可
    prev.next = l1 if l1 is not None else l2

    return prehead.next




def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
    # if not l1 and not l2: return None
    # if not l1 and l2: return l2
    # if l1 and not l2: return l1

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










