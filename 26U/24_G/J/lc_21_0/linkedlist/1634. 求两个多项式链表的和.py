# 1634. 求两个多项式链表的和


def addPoly(self, poly1: 'PolyNode', poly2: 'PolyNode') -> 'PolyNode':
    sent = cur = PolyNode()
    while poly1 or poly2:
        if not poly2 or (poly1 and poly1.power > poly2.power):
            cur.next = poly1
            cur = cur.next
            poly1 = poly1.next
        elif not poly1 or (poly2 and poly2.power > poly1.power):
            cur.next = poly2
            cur = cur.next
            poly2 = poly2.next
        else:
            cof = poly1.coefficient + poly2. coefficient
            if cof != 0:
                cur.next = PolyNode(cof, poly1.power)
                cur = cur.next
            poly1 = poly1.next
            poly2 = poly2.next
    cur.next = None
    return sent.next
        


def addPoly(self, poly1: 'PolyNode', poly2: 'PolyNode') -> 'PolyNode':
    dummy=PolyNode()
    head=dummy
    while poly1 or poly2:
        if not poly2 or (poly1 and poly1.power>poly2.power):
            head.next=poly1
            poly1=poly1.next
            head=head.next
        elif not poly1 or (poly1 and poly2.power>poly1.power):
            head.next=poly2
            poly2=poly2.next
            head=head.next
        else:
            c=poly1.coefficient+poly2.coefficient
            if c!=0:
                head.next=PolyNode(c,poly1.power)
                head=head.next
            poly1=poly1.next
            poly2=poly2.next
    head.next=None
    return dummy.next























