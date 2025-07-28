# 817. 链表组件

def numComponents(self, head: ListNode, G: List[int]) -> int:
    res = 0
    gset = set(G)
    while head:
        if head.val in gset:
            if not head.next or not head.next.val in gset:
                res += 1
        head = head.next
    return res



def numComponents(self, head, G):
    p, prev, count, G = head, False, 0, set(G)
    while p:
        if p.val in G and not prev:
            count += 1
        prev, p = p.val in G, p.next;
    
    return count
























