
160. 相交链表
LCR 023. 相交链表
def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> ListNode:
        if not headA or not headA:
            return None
        pa = headA
        pb = headB
        while pa != pb:
            pa = pa.next if pa else pb
            pb = pb.next if pb else pa
        return pa