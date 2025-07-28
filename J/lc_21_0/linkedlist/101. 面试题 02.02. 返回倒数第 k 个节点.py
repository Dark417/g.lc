"""
101. 面试题 02.02. 返回倒数第 k 个节点
剑指 Offer 22. 链表中倒数第k个节点

Given a linked list, remove the n-th node from the end of list and return its head.

Example:

Given linked list: 1->2->3->4->5, and n = 2.

After removing the second node from the end, the linked list becomes 1->2->3->5.
Note:

Given n will always be valid.

Follow up:

Could you do this in one pass?
"""


def getKthFromEnd(self, head: ListNode, k: int) -> ListNode:
    former, latter = head, head
    for _ in range(k):
        former = former.next
    while former:
        former, latter = former.next, latter.next
    return latter



def kthToLast(self, head: ListNode, k: int) -> int:
    start = end = head
    for i in range(k):
        end = end.next 
    while end:
        head = head.next
        end = end.next
    return head.val


def kthToLast(self, head: ListNode, k: int) -> int:
    fast = head
    slow = head
    while k > 0:
        fast = fast.next
        k -= 1
    while fast != None:
        fast = fast.next
        slow = slow.next
    return slow.val









































