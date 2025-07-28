# 1669. 合并两个链表
def mergeInBetween(self, list1: ListNode, a: int, b: int, list2: ListNode) -> ListNode:
    sent = ListNode(None)
    sent.next = cur = list1
    i = 0
    while i <= b:
        if i == a-1:
            tmp = cur
        cur = cur.next
        i += 1
    tmp.next = list2
    while list2.next:
        list2 = list2.next
    list2.next = cur
    return sent.next































