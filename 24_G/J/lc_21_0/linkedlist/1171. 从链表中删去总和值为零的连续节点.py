# 1171. 从链表中删去总和值为零的连续节点

def removeZeroSumSublists(self, head):
    cur = dummy = ListNode(0)
    dummy.next = head
    prefix = 0
    seen = collections.OrderedDict()
    while cur:
        prefix += cur.val
        node = seen.get(prefix, cur)
        while prefix in seen:
            seen.popitem()
        seen[prefix] = node
        node.next = cur = cur.next
    return dummy.next


def removeZeroSumSublists(self, head: ListNode) -> ListNode:
    dummy = ListNode(0)
    dummy.next = head
    prefix = 0
    d = {0:dummy} # key is the prefix sum, value is the last node of getting this sum value, which is l5
    while head:
        prefix += head.val
        d[prefix] = head
        head = head.next
    head = dummy
    prefix = 0
    while head:
        prefix += head.val
        head.next = d[prefix].next
        head = head.next
    return dummy.next


def removeZeroSumSublists(self, head: ListNode) -> ListNode:
	hashMap, runningSum = {}, 0
    cur = head 
    while cur:
        runningSum += cur.val
        if runningSum == 0:
            head = cur.next
        else:
            if runningSum not in hashMap:
                hashMap[runningSum] = cur 
            else:
                hashMap[runningSum].next = cur.next
        cur = cur.next
    return head



def removeZeroSumSublists(self, head: ListNode) -> ListNode:
    p = dummy = ListNode(0)
    dummy.next = head
    s = 0
    s_sum = [s]
    vals = {}
    while p:
        s += p.val
        s_sum.append(s)
        if s not in vals:
            vals[s] = p
        else:
            vals[s].next = p.next
            s_sum.pop() # remove cur, keep the last
            while s_sum[-1] != s:
                vals.pop(s_sum.pop())
        p = p.next
    return dummy.next




def removeZeroSumSublists(self, head: ListNode) -> ListNode:
    l = ListNode(0)
    l.next = head
    d = {0:l}
    s = 0
    while head:
        s+=head.val
        if s in d:
            d[s].next = head.next
            return self.removeZeroSumSublists(l.next)
        else:
            d[s] = head
            head = head.next
    return l.next














































