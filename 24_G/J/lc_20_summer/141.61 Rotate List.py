"""
141.61 Rotate List
旋转链表


Given a linked list, rotate the list to the right by k places, where k is non-negative.

Example 1:

Input: 1->2->3->4->5->NULL, k = 2
Output: 4->5->1->2->3->NULL
Explanation:
rotate 1 steps to the right: 5->1->2->3->4->NULL
rotate 2 steps to the right: 4->5->1->2->3->NULL
Example 2:

Input: 0->1->2->NULL, k = 4
Output: 2->0->1->NULL
Explanation:
rotate 1 steps to the right: 2->0->1->NULL
rotate 2 steps to the right: 1->2->0->NULL
rotate 3 steps to the right: 0->1->2->NULL
rotate 4 steps to the right: 2->0->1->NULL

"""










def rotateRight(self, head: 'ListNode', k: 'int') -> 'ListNode':
    # base cases
    if not head:
        return None
    if not head.next:
        return head
    
    # close the linked list into the ring
    old_tail = head
    n = 1
    while old_tail.next:
        old_tail = old_tail.next
        n += 1
    old_tail.next = head
    
    # find new tail : (n - k % n - 1)th node
    # and new head : (n - k % n)th node
    new_tail = head
    for i in range(n - k % n - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    
    # break the ring
    new_tail.next = None
    
    return new_head



def rotateRight(self, head: ListNode, k: int) -> ListNode:
    if not head or not head.next or not k: return head
    i = 0
    pre = cur = head
    while cur:
        cur = cur.next
        i += 1

    if k % i == 0: return head
    r = i - k % i - 1
    
    for _ in range(r):
        pre = pre.next
    start = cur = pre.next
    pre.next = None

    while cur.next:
        cur = cur.next
    cur.next = head

    return start


def rotateRight(self, head: ListNode, k: int) -> ListNode:
    if not head or k == 0:
        return head
    depth = 0
    tmp = head
    while tmp:
        depth+=1
        tmp = tmp.next
    k = k % depth
    if k == 0 or depth == 1:   ## 这里的条件需要特判，其实也是根据答案debug出来的
        return head
    # print(k, depth)
    # 需要起始动的位置是 
    res = head
    begin = depth - k
    dd = 0
    while dd < begin-1:
        dd += 1
        res = res.next
    cur = res.next
    res.next = None
    answer = cur
    while cur:
        if cur.next == None:
            break
        cur = cur.next
    cur.next = head

    return answer





















