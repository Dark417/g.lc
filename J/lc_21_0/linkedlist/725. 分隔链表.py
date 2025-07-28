# 725. 分隔链表

def splitListToParts(self, root, k):
    cur = root
    for N in xrange(1001):
        if not cur: break
        cur = cur.next
    width, remainder = divmod(N, k)

    ans = []
    cur = root
    for i in xrange(k):
        head = write = ListNode(None)
        for j in xrange(width + (i < remainder)):
            write.next = write = ListNode(cur.val) # write = write.next
            if cur: cur = cur.next
        ans.append(head.next)
    return ans



def splitListToParts(self, root, k):
    cur = root
    for N in xrange(1001):
        if not cur: break
        cur = cur.next
    width, remainder = divmod(N, k)

    ans = []
    cur = root
    for i in xrange(k):
        head = cur
        for j in xrange(width + (i < remainder) - 1):
            if cur: cur = cur.next
        if cur:
            cur.next, cur = None, cur.next
        ans.append(head)
    return ans




































