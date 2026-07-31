# 445. Add Two Numbers II 两数相加 II

def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
    s1, s2 = [], []
    while l1:
        s1.append(l1.val)
        l1 = l1.next
    while l2:
        s2.append(l2.val)
        l2 = l2.next
    ans = None
    carry = 0
    while s1 or s2 or carry != 0:
        a = 0 if not s1 else s1.pop()
        b = 0 if not s2 else s2.pop()
        cur = a + b + carry
        carry = cur // 10
        cur %= 10
        curnode = ListNode(cur)
        curnode.next = ans
        ans = curnode
    return ans

def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
    def helper(node1, node2, len1, len2, carry=0):
        if len1>len2:
            carry = helper(node1.next, node2, len1-1, len2)
            carry, node1.val = divmod(node1.val+carry, 10)
            return carry
        if len1>1:
            carry = helper(node1.next, node2.next, len1-1, len2-1)
        carry, node1.val = divmod(node1.val+node2.val+carry, 10)
        return carry

    len1 = len2 = 0
    node = l1
    while node:
        node, len1 = node.next, len1+1
    node = l2
    while node:
        node, len2 = node.next, len2+1
    if len1 < len2:
        l1, l2 = l2, l1
        len1, len2 = len2, len1
    carry = helper(l1, l2, len1, len2)
    if carry:
        head = ListNode(carry)
        head.next = l1
        return head
    else:
        return l1







def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        len1 = self._getLength(l1)
        len2 = self._getLength(l2)
        head, carry = self._addRecursively(l1, len1, l2, len2)
        if carry:
            head = ListNode(carry, head)
        return head
    
    def _addRecursively(self, l1: ListNode, len1: int, l2: ListNode, len2: int) -> ListNode:
        if not l1 and not l2:
            return (None, 0)
        current_sum = 0
        carry = 0
        if len1 > len2:
            head, carry = self._addRecursively(l1.next, len1 - 1, l2, len2)
            current_sum = l1.val + carry
        elif len1 < len2:
            head, carry = self._addRecursively(l1, len1, l2.next, len2 - 1)
            current_sum = l2.val + carry
        else:
            head, carry = self._addRecursively(l1.next, len1 - 1, l2.next, len2 - 1)
            current_sum = l1.val + l2.val + carry
        carry = current_sum // 10
        current_sum %= 10
        return (ListNode(current_sum, head), carry)

    def _getLength(self, l: ListNode) -> int:
        result = 0
        curr = l
        while curr:
            curr = curr.next
            result += 1
        return result



def addTwoNumbers(self, L1: ListNode, L2: ListNode) -> ListNode:
    S, A, B = 0, '', ''
    L = C = ListNode(0)
    while L1 != None: L1, A = L1.next, ''.join([A,str(L1.val)])
    while L2 != None: L2, B = L2.next, ''.join([B,str(L2.val)])
    S = str(int(A) + int(B))
    for d in S: C.next = ListNode(int(d)); C = C.next
    return L.next


def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
    pre = None
    cur = l1
    while cur:
        nxt = cur.next
        cur.next = pre
        pre = cur
        cur = nxt
    l3 = pre
    pre = None
    cur = l2
    while cur:
        nxt = cur.next
        cur.next = pre
        pre = cur
        cur = nxt
    l4 = pre
    dum = cur = ListNode(0)
    car = 0
    while l3 or l4 or car:
        if l3:
            car += l3.val
            l3 = l3.next
        if l4:
            car += l4.val
            l4 = l4.next
        cur.next = ListNode(car % 10)
        cur = cur.next
        car //= 10
    cur = dum.next
    pre = None
    while cur:
        nxt = cur.next
        cur.next = pre
        pre = cur
        cur = nxt
        
    return pre































