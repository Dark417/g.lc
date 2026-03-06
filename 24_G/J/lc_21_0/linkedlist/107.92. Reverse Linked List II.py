"""
107.92. Reverse Linked List II
反转链表 II


Reverse a linked list from position m to n. Do it in one-pass.

Note: 1 ≤ m ≤ n ≤ length of list.

Example:

Input: 1->2->3->4->5->NULL, m = 2, n = 4
Output: 1->4->3->2->5->NULL



https://leetcode-cn.com/problems/reverse-linked-list-ii/solution/fan-zhuan-lian-biao-ii-by-leetcode/
"""


# 前四个look look
# n - m / n - m + 1


# !! caikehe
def reverseBetween(self, head, m, n):
    dummy = pre = ListNode(0)
    dummy.next = head
    for _ in xrange(m-1):
        pre = pre.next
    cur= pre.next
    # reverse the defined part 
    node = None
    for _ in xrange(n-m+1):
        nxt = cur.next
        cur.next = node
        node = cur
        cur= nxt
    # connect three parts
    pre.next.next = cur     # 1->2 2=>5 1=>4
    pre.next = node
    return dummy.next




def reverseBetween(self, head, m, n):
    dummy = ListNode(0)
    dummy.next = head
    
    cur, prev = head, dummy
    for _ in xrange(m - 1):
        cur = cur.next
        prev = prev.next
    
    for _ in xrange(n - m):
        temp = cur.next
        cur.next = temp.next
        temp.next = prev.next
        prev.next = temp

    return dummy.next


def reverseBetween(self, head, m, n):
    if not head or m == n: return head
    p = dummy = ListNode(None)
    dummy.next = head
    for i in range(m-1): p = p.next
    tail = p.next

    for i in range(n-m):
        tmp = p.next                  # a)
        p.next = tail.next            # b)
        tail.next = tail.next.next    # c)
        p.next.next = tmp             # d)
    return dummy.next



def reverseBetween(self, head, m, n):
    if m >= n:
        return head
    #Step 1#    
    ohead = dummy = ListNode(0)
    whead = wtail = head
    dummy.next = head
    for i in range(n-m):
        wtail = wtail.next
    #Step 2#  
    for i in range(m-1):
        ohead, whead, wtail = whead, whead.next, wtail.next
    #Step 3#  
    otail, wtail.next = wtail.next, None
    revhead, revtail = self.reverse(whead)
    #Step 4#  
    ohead.next, revtail.next = revhead, otail
    return dummy.next
        
def reverse(self, head):
    pre, cur, tail = None, head, head
    while cur:
        cur.next, pre, cur = pre, cur, cur.next
    return pre, tail


def reverseBetween(self, head, m, n):
    if not head:
        return None

    left, right = head, head
    stop = False
    def recurseAndReverse(right, m, n):
        nonlocal left, stop
        if n == 1:
            return
        right = right.next
        if m > 1:
            left = left.next
        recurseAndReverse(right, m - 1, n - 1)
        if left == right or right.next == left:
            stop = True
        if not stop:
            left.val, right.val = right.val, left.val
            left = left.next           

    recurseAndReverse(right, m, n)
    return head


# zhou
def reverseBetween(self, head, m, n):
    # Edge
    if m == n: return head
    if not head or not m or not n: return None
    
    # Set starting point
    dummy = ListNode(0)
    dummy.next = head
    start = dummy
    for i in range(m - 1):
        start = start.next
        
    # Set ending point
    end = cur = start.next        
    
    prev = None
    # reverse
    for i in range(n - m + 1): 
        next = cur.next
        cur.next = prev
        prev = cur
        cur = next

    # Connect
    start.next = prev
    end.next = cur
    return dummy.next




def reverseBetween(self, head: ListNode, m: int, n: int) -> ListNode:
    s = pre = ListNode(0)
    s.next = cur = head
    for _ in range(m-1):
        pre = pre.next
        #cur = cur.next
    cur = pre.next
    start = pre
    end = cur
    pre = None
    for _ in range(n-m+1):
        next = cur.next
        cur.next = pre
        pre = cur
        cur = next
    end.next = cur
    start.next = pre
    return s.next



def reverseBetween(self, head: ListNode, m: int, n: int) -> ListNode:
    if not head: return None
    if m == n: return head
    c = 1
    cur = head
    while head:
        if c < m:
            start = tmp = cur
            end = start.next
        if c >= m and c < n:
            pre = cur
            next = cur.next.next
            cur.next.next = pre
            tmp.next = cur.next
            cur.next.next = next
        if c == n:
            start.next = tmp
            end.next = cur.next
            break
        cur = cur.next
        c += 1
    return head




def reverseBetween(self, head, m, n):
    if m >= n:
        return head
    #Step 1#    
    ohead = dummy = ListNode(0)
    whead = wtail = head
    dummy.next = head
    for i in range(n-m):
        wtail = wtail.next
    #Step 2#  
    for i in range(m-1):
        ohead, whead, wtail = whead, whead.next, wtail.next
    #Step 3#  
    otail, wtail.next = wtail.next, None
    revhead, revtail = self.reverse(whead)
    #Step 4#  
    ohead.next, revtail.next = revhead, otail
    return dummy.next
        
def reverse(self, head):
    pre, cur, tail = None, head, head
    while cur:
        cur.next, pre, cur = pre, cur, cur.next
    return pre, tail



def reverseBetween(self, head, m, n):
    if m == n:
        return head

    dummyNode = ListNode(0)
    dummyNode.next = head
    pre = dummyNode

    for i in range(m - 1):
        pre = pre.next
    
    # reverse the [m, n] nodes
    reverse = None
    cur = pre.next
    for i in range(n - m + 1):
        next = cur.next
        cur.next = reverse
        reverse = cur
        cur = next

    pre.next.next = cur
    pre.next = reverse

    return dummyNode.next







def reverseBetween(self, head, m, n):
    if m==n:
        return head
    # Consider linked list as a list A. i.e. A[1]=head.val, A[2]=head.next.val ....
    # Create dummy.         [D,A[1],A[2],....]        
    dummy=ListNode(0)
    dummy.next=head
    # c at A[0]
    c=dummy

    # move c m-1 times. now c is at A[M-1]
    for _ in range(m-1):
        c=c.next

    # start reversing from s=c.next (A[M]) for n-m+1 nodes
    s,r=c.next,None
    for _ in range(n-m+1):
        s.next,s,r=r,s.next,s

    # now the situation is
    # [dummy .... c]    [r,..., c.next]   [s .....]
    # connect c to r, and c.next to s


    # careful. c.next,c.next.next=r,s gives you an error
    c.next.next,c.next=s,r

    return dummy.next








# official
def reverseBetween(self, head, m, n):
    # Empty list
    if not head:
        return None

    # Move the two pointers until they reach the proper starting point
    # in the list.
    cur, prev = head, None
    while m > 1:
        prev = cur
        cur = cur.next
        m, n = m - 1, n - 1

    # The two pointers that will fix the final connections.
    tail, con = cur, prev

    # Iteratively reverse the nodes until n becomes 0.
    while n:
        third = cur.next
        cur.next = prev
        prev = cur
        cur = third
        n -= 1

    # Adjust the final connections as explained in the algorithm
    if con:
        con.next = prev
    else:
        head = prev
    tail.next = cur
    return head




"""
1.首先找到需要翻转的位置，在这个位置做标记（记作pre）
2.在m <= count <= n 的时候对链表进行翻转（记作rev）
3.连接三部分，pre + rev + >n的剩余节点，如果m = 1，那么只有rev + >n的剩余节点
"""

def reverseBetween(self, head: ListNode, m: int, n: int) -> ListNode:
    if not head or not head.next:
        return head
    pre = None  # <m的部分
    rev = None  # 1<= m <= n 的部分,即需要翻转的部分
    pRev = None # 翻转链表中的首个节点，翻转完成以后就指向链表的最后一个节点，用于连接>n的剩余部分
    p = head
    count = 1
    while p:
        if count > n:   # >n以后不操作，直接链接（pre + rev + >n的部分节点）
            break
        if count >= m:  # 在翻转范围，对指定部分进行翻转
            tmp = p.next
            p.next = rev    
            rev = p
            if not pRev:    # 翻转链表的指针，用于链接break以后剩余的链表，只需要指向第一个翻转节点，后续不重新赋值
                pRev = rev
            p = tmp
        else:    # 当count > m以后，pre节点不需要再往后追踪，只追踪至开始翻转的节点的前一个节点即可
            pre = p
            p = p.next
        count += 1
    pRev.next = p   # 把翻转后的链表最后一个指针指向剩余head部分
    if pre: # 如果pre指针有值，则m>1，要把前中后三部分连接起来
        pre.next = rev
        return head
    else:   # 如果pre指针为空，则说明m = 1，一开始就要翻转，只需要返回中后部分，即rev + >n的部分，没有pre
        return rev






# D1
def reverseBetween(self, head: ListNode, m: int, n: int) -> ListNode:
    sent = first = pre = ListNode(None)
    sent.next = cur = start = head
    
    for _ in range(1, m):
        first = cur
        start = cur.next
        cur = cur.next
        
    for _ in range(n - m + 1):
        nxt = cur.next
        second = nxt
        cur.next = pre
        pre = cur
        cur = nxt
        
    first.next = pre
    start.next = second
    return sent.next

# D2
def reverseBetween(self, head: ListNode, m: int, n: int) -> ListNode:
    sent = pre = first = ListNode(None)
    sent.next = cur = start = head
    i = 1
    while cur and i <= n:
        if i < m:
            i += 1
            first = cur
            start = cur.next
            cur = cur.next
        else:
            nxt = cur.next
            second = nxt
            cur.next = pre
            pre = cur
            cur = nxt
            i += 1
    first.next = pre
    start.next = second
    return sent.next































