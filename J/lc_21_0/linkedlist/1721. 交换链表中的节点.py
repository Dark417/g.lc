# 1721. 交换链表中的节点

def swapNodes(self, head: ListNode, k: int) -> ListNode:
    n1, n2, p = None, None, head
    while p is not None:
        k -= 1
        n2 = None if n2 == None else n2.next
        if k == 0:
            n1 = p
            n2 = head
        p = p.next
    n1.val, n2.val = n2.val, n1.val
    return head


def swapNodes(self, head: ListNode, k: int) -> ListNode:
	
    slow, fast = head, head
	
    for _ in range(k - 1):
        fast = fast.next
    first = fast

    while fast.next:
        slow, fast = slow.next, fast.next
	
    first.val, slow.val = slow.val, first.val

    return head


def swapNodes(self, head: ListNode, k: int) -> ListNode:
    p,q,n=head,head,head
    i=1
    while n:
        if i<k:
            p=p.next#正数第k个
        if i>k:
            q=q.next#倒数第k个
        n=n.next
        i+=1
    p.val,q.val=q.val,p.val
    return head


        
def swapNodes(self, head: ListNode, k: int) -> ListNode:
    walker = runner = first = dummy = ListNode(next=head)
    for i in range(k):
        first = runner
        runner = runner.next
    while runner.next:
        walker = walker.next
        runner = runner.next
    left, right = first.next, walker.next
    if right.next is left:
        left, right = right, left
        first, walker = walker, first
    left_next, right_next = left.next, right.next
    if left_next is right:
        first.next = right
        right.next = left
        left.next = right_next
    else:
        first.next, walker.next = right, left
        right.next, left.next = left_next, right_next
    return dummy.next




































